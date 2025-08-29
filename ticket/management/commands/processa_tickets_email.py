from django.core.management.base import BaseCommand
from ticket.scripts.processar_emails import processar_emails  # ou ajuste o import se o caminho for diferente

class Command(BaseCommand):
    help = 'Processa e-mails recebidos para criar tickets'

    def handle(self, *args, **kwargs):
        processar_emails()
        self.stdout.write(self.style.SUCCESS('Tickets criados a partir de e-mails!'))

