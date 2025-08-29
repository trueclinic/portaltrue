from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Ticket(models.Model):
    PRIORIDADES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
    ]

    STATUS = [
        ('aberto', 'Aberto'),
        ('em_andamento', 'Em andamento'),
        ('resolvido', 'Resolvido'),
        ('fechado', 'Fechado'),
    ]

    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    prioridade = models.CharField(max_length=10, choices=PRIORIDADES, default='media')
    status = models.CharField(max_length=15, choices=STATUS, default='aberto')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets_criados')
    atribuido_para = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='tickets_atribuidos'
)
    reporter_nome = models.CharField(max_length=255, null=True, blank=True)
    reporter_email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"{self.titulo} ({self.status})"

    @property
    def ultima_interacao(self):
        """Retorna a data/hora da última interação no ticket.
        Considera atualização do próprio ticket, comentários e anexos.
        """
        datas = [self.atualizado_em]
        try:
            c = self.comentarios.order_by('-criado_em').values_list('criado_em', flat=True).first()
            if c:
                datas.append(c)
        except Exception:
            pass
        try:
            a = self.anexos.order_by('-enviado_em').values_list('enviado_em', flat=True).first()
            if a:
                datas.append(a)
        except Exception:
            pass
        return max(datas) if datas else self.criado_em


class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    mensagem = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em']

    def __str__(self):
        return f"Comentário #{self.id} no ticket #{self.ticket_id}"


class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='anexos')
    ficheiro = models.FileField(upload_to='tickets/')
    enviado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    enviado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Anexo #{self.id} do ticket #{self.ticket_id}"