from django.core.management.base import BaseCommand
from ticket.scripts.processar_emails_graph import processar_emails_graph


class Command(BaseCommand):
    help = 'Processa e-mails via Microsoft Graph e cria tickets'

    def handle(self, *args, **kwargs):
        created = processar_emails_graph()
        self.stdout.write(self.style.SUCCESS(f'Tickets criados: {created}'))
