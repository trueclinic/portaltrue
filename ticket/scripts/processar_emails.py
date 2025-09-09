import imaplib
import email
from email.header import decode_header
from django.contrib.auth.models import User
from ticket.models import Ticket
from django.core.mail import send_mail
from django.conf import settings
from decouple import config

def processar_emails():
    # Configuração do e-mail (parametrizada via env)
    HOST = config('IMAP_HOST', default='outlook.office365.com')
    EMAIL = config('IMAP_USER', default=settings.EMAIL_HOST_USER)
    SENHA = config('IMAP_PASSWORD')

    # Conectar ao servidor IMAP
    mail = imaplib.IMAP4_SSL(HOST)
    mail.login(EMAIL, SENHA)
    mail.select('INBOX')

    # Buscar e-mails não lidos
    status, messages = mail.search(None, '(UNSEEN)')
    email_ids = messages[0].split()

    for e_id in email_ids:
        _, data = mail.fetch(e_id, '(RFC822)')
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        from_email = email.utils.parseaddr(msg['From'])[1]
        subject = msg['Subject']
        body = ""

        if msg.is_multipart():
            # Prioriza text/plain; se não houver, tenta text/html como fallback simples
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    body = part.get_payload(decode=True).decode(errors='ignore')
                    break
            if not body:
                for part in msg.walk():
                    if part.get_content_type() == 'text/html':
                        html = part.get_payload(decode=True).decode(errors='ignore')
                        # Remoção simples de tags para extrair texto
                        body = email.utils.unquote(html)
                        break
        else:
            payload = msg.get_payload(decode=True)
            body = (payload.decode(errors='ignore') if isinstance(payload, (bytes, bytearray)) else str(payload))

        # Verifica se o remetente está registado
        try:
            user = User.objects.get(email__iexact=from_email)
        except User.DoesNotExist:
            # Em desenvolvimento, opcionalmente faz fallback para um utilizador padrão
            if settings.DEBUG:
                # Usa o primeiro superuser/staff disponível ou cria um utilizador de fallback
                user = (
                    User.objects.filter(is_superuser=True).first()
                    or User.objects.filter(is_staff=True).first()
                )
                if not user:
                    user, _ = User.objects.get_or_create(
                        username='dev-mail',
                        defaults={'email': settings.EMAIL_HOST_USER or 'dev@example.com', 'is_staff': True}
                    )
            else:
                # Em produção, ignora remetentes desconhecidos
                continue

        # Criar o ticket
        ticket = Ticket.objects.create(
            titulo=subject or "Problema reportado via e-mail",
            descricao=body,
            criado_por=user,
            prioridade='media',
            status='aberto',
            reporter_nome=(user.get_full_name() or user.username),
            reporter_email=from_email
        )

        # Envia resposta com número do ticket
        send_mail(
            subject=f"Ticket #{ticket.id} aberto com sucesso",
            message=f"Olá {user.get_full_name() or user.username},\n\nRecebemos o seu pedido. O número do ticket é #{ticket.id}.\n\nA nossa equipa irá responder em breve.\n\nObrigado.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[from_email],
            fail_silently=False,
        )

    mail.logout()
