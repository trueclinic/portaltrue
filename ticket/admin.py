from django.contrib import admin
from .models import Ticket

# Register your models here.

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'prioridade', 'status', 'criado_por', 'atribuido_para', 'criado_em')
    list_filter = ('status', 'prioridade')
    search_fields = ('titulo', 'descricao')