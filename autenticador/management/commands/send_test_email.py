import os
import ssl
import smtplib
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import certifi


def patch_starttls_with_certifi() -> None:
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    original_starttls = smtplib.SMTP.starttls

    def starttls(self, *args, **kwargs):
        kwargs["context"] = ssl_context
        return original_starttls(self, *args, **kwargs)

    smtplib.SMTP.starttls = starttls


class Command(BaseCommand):
    help = "Envia um e-mail de teste usando as configurações atuais"

    def add_arguments(self, parser):
        parser.add_argument(
            "recipient",
            nargs="?",
            default=None,
            help="E-mail de destino (padrão: EMAIL_HOST_USER)",
        )
        parser.add_argument(
            "--no-certifi",
            action="store_true",
            help="Não aplicar correção de SSL com certifi (útil se já configurado no SO)",
        )

    def handle(self, *args, **options):
        recipient = options["recipient"] or settings.EMAIL_HOST_USER
        use_certifi = not options["no_certifi"]

        # Corrige SSL em ambientes locais/macOS quando necessário
        if use_certifi:
            patch_starttls_with_certifi()

        try:
            sent = send_mail(
                subject="[PortalTrue] Teste de e-mail",
                message="Envio de teste via comando de management.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f"Emails enviados: {sent}"))
        except Exception as exc:
            self.stdout.write(self.style.ERROR(f"Falha no envio: {type(exc).__name__}: {exc}"))


