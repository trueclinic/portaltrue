from django.contrib import admin
from .models import  NomeExame, Utilizador, Departamento, emailstrue, Licencas, Fornecedor, Marca, Modelo, PlanosTelemoveis, Nome_Equipamento_1


#Classes do admin
class NomeExameAdmin(admin.ModelAdmin):
    list_display = ('nome_exame', 'id','registado')

class UtilizadorAdmin(admin.ModelAdmin):
    list_display = ('nome_utilizador', 'departamento_utilizador', 'utilizador_plataforma', 'id')

class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nome_departamento', 'id','registado')

class emailstrueAdmin(admin.ModelAdmin):
    list_display = ('email', 'id', 'registado')

class LicencasAdmin(admin.ModelAdmin):
    list_display = ('tipo_licenca', 'id', 'registado')

class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome_fornecedor', 'id', 'registado')

class MarcaAdmin(admin.ModelAdmin):
    list_display = ('marca_equipamento', 'id', 'registado')

class ModeloAdmin(admin.ModelAdmin):
    list_display = ('modelo_equipamento', 'id', 'registado')

class PlanosTelemoveisAdmin(admin.ModelAdmin):
    list_display = ('plano', 'valor', 'id', 'registado')

class NomeEquipamento_1Admin(admin.ModelAdmin):
    list_display = ('nome_equipamento', 'id','registado')



# Register your models here.
admin.site.register(NomeExame, NomeExameAdmin)
admin.site.register(Utilizador, UtilizadorAdmin)
admin.site.register(Departamento, DepartamentoAdmin)
admin.site.register(emailstrue, emailstrueAdmin)
admin.site.register(Licencas, LicencasAdmin)
admin.site.register(Fornecedor, FornecedorAdmin)
admin.site.register(Marca, MarcaAdmin)
admin.site.register(Modelo, ModeloAdmin)
admin.site.register(PlanosTelemoveis, PlanosTelemoveisAdmin)
admin.site.register(Nome_Equipamento_1, NomeEquipamento_1Admin)

