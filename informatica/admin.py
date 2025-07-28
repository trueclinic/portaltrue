from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Inventario,
    EmailCompartilhado,
    AparelhoTelemovel,
    InventarioEquipamento,
    Equipamentos,
    CartaoTelemovel
)

# Inlines
class EmailCompartilhadoInline(admin.TabularInline):
    model = EmailCompartilhado
    extra = 1

class EquipamentoInline(admin.TabularInline):
    model = Equipamentos
    extra = 1

# Admins
@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('nome_utilizador', 'registado', 'editado')
    inlines = [EmailCompartilhadoInline, EquipamentoInline]

@admin.register(CartaoTelemovel)
class CartaoTelemovelAdmin(admin.ModelAdmin):
    list_display = ('atribuido', 'numero_telefone', 'numero_cartao')

@admin.register(AparelhoTelemovel)
class AparelhoTelemovelAdmin(admin.ModelAdmin):
    list_display = ('estatus_telemovel', 'atribuido_1', 'marca_esquipamento', 'modelo_esquipamento')

@admin.register(InventarioEquipamento)
class InventarioEquipamentoAdmin(admin.ModelAdmin):
    list_display = ('nome_equipamento', 'atribuido', 'estatus_equipamento', 'ver_fatura')

    def ver_fatura(self, obj):
        if obj.fatura:
            return format_html('<a href="{}" target="_blank">Ver Fatura</a>', obj.fatura.url)
        return 'Sem fatura'

    ver_fatura.short_description = 'Fatura'

@admin.register(Equipamentos)
class EquipamentosAdmin(admin.ModelAdmin):
    list_display = ('nome_equipamento', 'nome_utilizador')
