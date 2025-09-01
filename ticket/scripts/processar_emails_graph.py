import os
from typing import List
import msal
import requests
from decouple import config
from django.contrib.auth.models import User
from ticket.models import Ticket
from django.core.mail import send_mail
from django.conf import settings


GRAPH_TENANT_ID = config("GRAPH_TENANT_ID")
GRAPH_CLIENT_ID = config("GRAPH_CLIENT_ID")
GRAPH_CLIENT_SECRET = config("GRAPH_CLIENT_SECRET")
GRAPH_USER_ID = config("GRAPH_USER_ID", default=settings.EMAIL_HOST_USER)


def _get_access_token() -> str:
    authority = f"https://login.microsoftonline.com/{GRAPH_TENANT_ID}"
    app = msal.ConfidentialClientApplication(
        client_id=GRAPH_CLIENT_ID,
        client_credential=GRAPH_CLIENT_SECRET,
        authority=authority,
    )
    scope = ["https://graph.microsoft.com/.default"]
    result = app.acquire_token_silent(scopes=scope, account=None)
    if not result:
        result = app.acquire_token_for_client(scopes=scope)
    if "access_token" not in result:
        raise RuntimeError(f"Falha ao obter token: {result}")
    return result["access_token"]


def _graph_get(url: str) -> dict:
    token = _get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _graph_post(url: str, json: dict) -> dict:
    token = _get_access_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json=json, timeout=30)
    resp.raise_for_status()
    return resp.json() if resp.text else {}


def processar_emails_graph() -> int:
    """Lê mensagens não lidas na caixa e cria tickets.

    Requer permissões: Mail.Read, Mail.ReadWrite, Mail.Send (Application) no Graph.
    GRAPH_USER_ID pode ser UPN (e-mail) ou id do user no Entra ID.
    """
    base = "https://graph.microsoft.com/v1.0"
    # Buscar mensagens não lidas
    url = (
        f"{base}/users/{GRAPH_USER_ID}/mailFolders/Inbox/messages?"
        "$filter=isRead eq false&$top=10&$select=id,subject,from,bodyPreview"
    )
    data = _graph_get(url)
    messages = data.get("value", [])
    created = 0
    for msg in messages:
        msg_id = msg["id"]
        subject = msg.get("subject") or "Problema reportado via e-mail"
        sender = (msg.get("from") or {}).get("emailAddress", {}).get("address")
        body_preview = msg.get("bodyPreview") or ""

        if not sender:
            # marca como lida e continua
            _graph_post(f"{base}/users/{GRAPH_USER_ID}/messages/{msg_id}/read", {})
            continue

        try:
            user = User.objects.get(email__iexact=sender)
        except User.DoesNotExist:
            # marca como lida e ignora
            _graph_post(f"{base}/users/{GRAPH_USER_ID}/messages/{msg_id}/read", {})
            continue

        ticket = Ticket.objects.create(
            titulo=subject,
            descricao=body_preview,
            criado_por=user,
            prioridade='media',
            status='aberto',
        )
        created += 1

        # Responde confirmando
        send_mail(
            subject=f"Ticket #{ticket.id} aberto com sucesso",
            message=(
                f"Olá {user.get_full_name() or user.username},\n\n"
                f"Recebemos o seu pedido. O número do ticket é #{ticket.id}.\n\n"
                "Obrigado."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[sender],
            fail_silently=False,
        )

        # Marca como lida
        _graph_post(f"{base}/users/{GRAPH_USER_ID}/messages/{msg_id}/read", {})

    return created
