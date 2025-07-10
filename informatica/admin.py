from sre_constants import IN
from django.contrib import admin
from .models import Inventario, EmailCompartilhado, AparelhoTelemovel, InventarioEquipamento, Equipamentos, CartaoTelemovel

# ---- Class do Admin ----------------------------------------------------------------------------#
class EmailCompartilhadoInLine(admin.TabularInline):
    model = EmailCompartilhado
    extra = 1

class EquipamentoInLine(admin.TabularInline):
    model = Equipamentos
    extra = 1

class AparelhoTelemovelInline(admin.TabularInline):
    list_display = ('atribuido', 'numero_cartao', 'plano')
    model = AparelhoTelemovel
    extra = 1

class InventarioAdmin(admin.ModelAdmin):
    list_display = ('nome_utilizador', 'registado', 'editado', 'id')
    search_fields = ('nome_utilizador', 'departamento')
   

    inlines = [
        EmailCompartilhadoInLine,
        EquipamentoInLine,
        AparelhoTelemovelInline
    ]


# Register your models here

admin.site.register(Inventario, InventarioAdmin)
admin.site.register(InventarioEquipamento)
admin.site.register(CartaoTelemovel)