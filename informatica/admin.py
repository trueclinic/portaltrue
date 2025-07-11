from django.contrib import admin
from .forms import InventarioEquipamentoForm
from django.utils.html import format_html
from .models import (
    Inventario,
    EmailCompartilhado,
    AparelhoTelemovel,
    InventarioEquipamento,
    Equipamentos,
    CartaoTelemovel
)

# ---------------------- Inlines ----------------------

class EmailCompartilhadoInline(admin.TabularInline):
    model = EmailCompartilhado
    extra = 1

class EquipamentoInline(admin.TabularInline):
    model = Equipamentos
    extra = 1

class AparelhoTelemovelInline(admin.TabularInline):
    model = AparelhoTelemovel
    extra = 1

# ---------------------- Admins -----------------------

@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('nome_utilizador', 'registado', 'editado', 'id')
    search_fields = ('nome_utilizador', 'departamento')
    inlines = [
        EmailCompartilhadoInline,
        EquipamentoInline,
        AparelhoTelemovelInline
    ]

@admin.register(CartaoTelemovel)
class CartaoTelemovelAdmin(admin.ModelAdmin):
    list_display = ('atribuido', 'numero_telefone', 'id', 'registado')

@admin.register(InventarioEquipamento)
class InventarioEquipamentoAdmin(admin.ModelAdmin):
    form = InventarioEquipamentoForm

    fieldsets = (
        ('Informações Gerais', {
            'fields': (
                'estatus_equipamento',
                'nome_equipamento',
                'atribuido_check',
                'atribuido',
                'descricao_equipamento',
            )
        }),
        ('Memória', {
            'fields': (
                'memoria_select',
                'memoria',
            )
        }),
        ('Rede e IP', {
            'fields': (
                'tipo_ip_select',
                'numero_ip',
                'nome_rede',
                'mac',
            )
        }),
        ('Dados Técnicos', {
            'fields': (
                'marca_esquipamento',
                'modelo_esquipamento',
                'numero_serie',
                'sistema_operacional',
            )
        }),
        ('Fornecedor e Garantia', {
            'fields': (
                'fornecedor',
                'data_compra',
                'data_garantia',
                'tipo_garantia',
                'fatura',
                'download_fatura',  # adiciona aqui para aparecer no detalhe do admin
            )
        }),
        ('Observações', {
            'fields': (
                'observacoes',
            )
        }),
        ('Registo', {
            'fields': (
                'registado',
                'editado',
            )
        }),
    )

    readonly_fields = ('registado', 'editado', 'download_fatura')

    # Opcional: mostrar link na lista
    list_display = ('nome_equipamento', 'atribuido', 'estatus_equipamento', 'download_fatura')

    def download_fatura(self, obj):
        if obj.fatura:
            return format_html(
                '<a href="{}" download>📎 Baixar Fatura</a>',
                obj.fatura.url
            )
        return "Sem fatura"

    download_fatura.short_description = "Fatura"

    class Media:
        js = ('admin/js/inventario_custom.js',)