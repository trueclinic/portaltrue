from django.contrib import admin
from .models import NomeSinistrado, RegistoExames

# ---- Class do Admin ----------------------------------------------------------------------------#
class RegistoExamesInline(admin.TabularInline):
    model = RegistoExames
    extra = 0

class NomeSinistradoAdmin(admin.ModelAdmin):
    list_display = ('nome_sinistrado', 'numero_nif', 'registado')
    search_fields = ('nome_sinistrado', 'numero_nif')
    list_filter = ('nome_sinistrado', 'numero_nif')
    inlines = [
        RegistoExamesInline
    ]

# Register your models here.

admin.site.register(NomeSinistrado, NomeSinistradoAdmin)

