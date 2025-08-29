import imaplib
import email
from email.header import decode_header
from django.contrib.auth.models import User
from ticket.models import Ticket
from django.core.mail import send_mail
from django.conf import settings

def processar_emails():
    # Configuração do e-mail
    HOST = 'outlook.office365.com'  # ou outro endereço IMAP
    EMAIL = 'suportetecnico@trueclinic.pt'
    SENHA = 'kywvrvkmlqckzjzl'

    # Conectar ao servidor IMAP
    mail = imaplib.IMAP4_SSL(HOST)
    mail.login(EMAIL, SENHA)
    mail.select('inbox')

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
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()

        # Verifica se o remetente está registado
        try:
            user = User.objects.get(email=from_email)
        except User.DoesNotExist:
            continue  # Ignora se o remetente não for conhecido

        # Criar o ticket
        ticket = Ticket.objects.create(
            titulo=subject or "Problema reportado via e-mail",
            descricao=body,
            criado_por=user,
            prioridade='media',
            status='aberto'
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
