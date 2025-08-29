from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Cria um utilizador de desenvolvimento com email e palavra‑passe fornecidos.'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True)
        parser.add_argument('--username', required=False)
        parser.add_argument('--password', required=True)
        parser.add_argument('--staff', action='store_true', default=False, help='Define o utilizador como staff')

    def handle(self, *args, **opts):
        email = opts['email'].strip().lower()
        username = (opts.get('username') or email.split('@')[0]).strip()
        password = opts['password']

        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        if not created:
            user.email = email
        user.is_staff = bool(opts.get('staff'))
        user.is_superuser = False
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Utilizador {'criado' if created else 'atualizado'}: {username} <{email}>"))



