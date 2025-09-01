import os
import ssl
import smtplib

# Garantir que o Django carrega as settings do projeto
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Evitar bloqueio de import por variáveis Cloudinary ausentes em ambiente local
os.environ.setdefault("CLOUDINARY_CLOUD_NAME", "dummy")
os.environ.setdefault("CLOUDINARY_API_KEY", "dummy")
os.environ.setdefault("CLOUDINARY_API_SECRET", "dummy")

from django.conf import settings
from django.core.mail import EmailMessage
import certifi


def patch_starttls_with_certifi() -> None:
    """Força o uso do bundle de certificados do certifi no starttls (macOS)."""
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    original_starttls = smtplib.SMTP.starttls

    def starttls(self, *args, **kwargs):
        kwargs["context"] = ssl_context
        return original_starttls(self, *args, **kwargs)

    smtplib.SMTP.starttls = starttls


def main() -> None:
    patch_starttls_with_certifi()
    print("Local -> host:", settings.EMAIL_HOST, "user:", settings.EMAIL_HOST_USER)
    msg = EmailMessage(
        subject="[PortalTrue] Teste LOCAL",
        body="Envio de teste local.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=["suportetecnico@trueclinic.pt"],
    )
    sent = msg.send(fail_silently=False)
    print("Emails enviados:", sent)


if __name__ == "__main__":
    main()


