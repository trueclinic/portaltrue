import email
from email.errors import NonASCIILocalPartDefect
from operator import mod
from platform import mac_ver
import re
from socket import NI_NUMERICHOST
from threading import activeCount
from django.db import models
from comum.models import Marca, Modelo, emailstrue, PlanosTelemoveis, Fornecedor, Utilizador, Nome_Equipamento_1, Nome_SO

#-------------------------------- Signals -------------------------------------------------#
from django.db.models import signals
from django.template.defaultfilters import slugify

# Create your models here.


#-------------------------------- Choices -------------------------------------------------#

tipo_IP_choices = [
    ('Fixo', 'Fixo'),
    ('Dinâmico', 'Dinâmico'),
]

versao_IP_choices = [
    ('IPV4', 'IPV4'),  
    ('IPV6', 'IPV6'),
]

setor_choises = [
    ('Gestão', 'Gestão'),
    ('Financeiro', 'Financeiro'), 
    ('Profissional', 'Profissional'), 
    ('Diretoria', 'Diretoria'),
    ('Informática', 'Informática'), 
    ('Clínica', 'Clínica'),
    ('Administração', 'Administração'),
]

STATUS_CHOICES = [
        ('em_uso', 'Em Uso'),
        ('desuso', 'Desuso'),
        ('descartado', 'Descartado'),
    ]
tipo_armazenamento_choices = [
    ('HD', 'HD'),
    ('SSD', 'SSD'),
]

tipo_garantia_choices = [
    ('Balcão', 'Balcão'),
    ('On Site', 'On Site'),
]

acessos_choices = [
    ('Partilha', 'Partilha'),
    ('Plataforma', 'Plataforma'),
    ('User Site', 'User Site'),
    ('4Admin Site', 'Admin Site'),
]
tag_porta_choices = [
    ('Tag', 'Tag'),
    ('Chave', 'Chave'),
    ('Não', 'Não'),
]



#-------------------------------- FimChoices -------------------------------------------------#

# ---- Utilizadores ----------------------------------------------------------------------------#

class Inventario(models.Model):
    id = models.BigAutoField(primary_key=True)
    registado = models.DateTimeField(auto_now_add=True, verbose_name='Registado em:')
    editado = models.DateTimeField(auto_now_add=True, verbose_name='Alterado em: ')

    nome_utilizador = models.ForeignKey(Utilizador, on_delete=models.PROTECT, verbose_name='Nome do Utilizador')
    
    tag_da_porta = models.BooleanField(default=False, verbose_name='Tag da porta')
    numero_tag = models.CharField(max_length=50, blank=True, null=True, verbose_name='Número da TAG')

    email_pessoal = models.ForeignKey(emailstrue, on_delete=models.PROTECT, verbose_name='E-mail Pessoal', blank=True)

    class Meta:
        verbose_name_plural = 'Inventário'

    def __str__(self):
        return '{}'.format(self.nome_utilizador)


# ---- Emails Compartilhados ----------------------------------------------------------------------------#

class EmailCompartilhado(models.Model):
 #  Nome Campo                          Tipo Model              Atributos    
    id                              = models.BigAutoField   (primary_key=True)
    registado                       = models.DateTimeField  (auto_now_add=True, verbose_name='Registado em:')
    editado                         = models.DateTimeField  (auto_now_add=True, verbose_name='Alterado em: ')
    email_compartilhado             = models.ForeignKey     (emailstrue, on_delete=models.PROTECT, verbose_name='Email')
    # Campo derivado de outro campo
    email_pessoal                   = models.ForeignKey     (Inventario, on_delete=models.PROTECT)


    class Meta:
        verbose_name_plural = ('Emails Compartilhados')
    def __str__(self):
        return '{}'.format(self.email_compartilhado)



# ---- Inventarios Equipamentos --------------------------------------------------------------------#        
class InventarioEquipamento(models.Model):

    id                              = models.BigAutoField   (primary_key=True)
    registado                       = models.DateTimeField  (auto_now_add=True, verbose_name='Registado em:')
    editado                         = models.DateTimeField  (auto_now_add=True, verbose_name='Alterado em: ')
    estatus_equipamento             = models.CharField      (max_length=10, choices=STATUS_CHOICES, default='em_uso', verbose_name='Estatus')
    nome_equipamento                = models.ForeignKey     (Nome_Equipamento_1, on_delete=models.PROTECT, verbose_name='Nome do Equipamento', blank=False)
    atribuido_check                 = models.BooleanField   (default=False, verbose_name='Atribuído?')
    atribuido                       = models.ForeignKey     (Utilizador, on_delete=models.PROTECT, blank=True, null=True, verbose_name='Utilizador')
    descricao_equipamento           = models.TextField      (verbose_name='Descrição do Equipamento', blank=True)
    nome_rede                       = models.CharField      (max_length=20, verbose_name='Nome na Rede', blank=True, unique=True)
    # Campo derivado de outro campo
    marca_esquipamento              = models.ForeignKey     (Marca, on_delete=models.PROTECT, verbose_name='Marca do Esquipamento')
    # Campo derivado de outro campo
    modelo_esquipamento             = models.ForeignKey     (Modelo, on_delete=models.PROTECT, verbose_name='Modelo do Equipamento')
    numero_serie                    = models.CharField      (max_length=50, verbose_name='Número de Série', unique=True)
    sistema_operacional             = models.ForeignKey     (Nome_SO, on_delete=models.PROTECT, verbose_name='Sistema Operacional')
    memoria                         = models.CharField      (max_length=20, verbose_name='Memoria', blank=True)
    numero_ip                       = models.CharField      (max_length=50, verbose_name='Número do IP', blank=True)
    mac                             = models.CharField      (max_length=30, verbose_name='Mac Address', blank=True)
    fornecedor                      = models.ForeignKey     (Fornecedor, on_delete=models.PROTECT, verbose_name='Fornecedor')
    data_compra                     = models.DateField      (auto_now_add=False, verbose_name='Data da Compra')
    data_garantia                   = models.DateField      (auto_now_add=False, verbose_name='Final da Garantia')
    tipo_garantia                   = models.CharField      (max_length=10, choices=tipo_garantia_choices, verbose_name='Tipo de Garantia', blank=True)
    fatura                          = models.FileField      (upload_to='%Y/%m/%d/', blank=True, verbose_name='Fatura de Compra')
    observacoes                     = models.TextField      (verbose_name='Observações Gerais', blank=True)


    class Meta:
        verbose_name_plural = ( 'Equipamentos TrueClinic')

    def __str__(self):
        return '{} | {} | {} | {} | {}' .format(self.atribuido, self.nome_equipamento, self.nome_rede, self.marca_esquipamento, self.modelo_esquipamento)

# ---- Equipamento --------------------------------------------------------------------#
class Equipamentos(models.Model):
    id                              = models.BigAutoField   (primary_key=True)
    registado                       = models.DateTimeField  (auto_now_add=True, verbose_name='Registado em:')
    editado                         = models.DateTimeField  (auto_now_add=True, verbose_name='Alterado em: ')
    # Campo derivado de outro campo
    nome_equipamento                = models.ForeignKey     (InventarioEquipamento, on_delete=models.PROTECT, verbose_name='Equipamento')
    # Campo derivado de outro campo
    nome_utilizador                 = models.ForeignKey     (Inventario, on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = ('Equipamentos')

    def __str__(self):
        return '{}' .format(self.nome_equipamento)
    

# ---- Telemóveis TrueClinic ----------------------------------------------------------------------------#
class CartaoTelemovel(models.Model):
    id                              = models.BigAutoField   (primary_key=True)
    registado                       = models.DateTimeField  (auto_now_add=True, verbose_name='Registado em:')
    editado                         = models.DateTimeField  (auto_now_add=True, verbose_name='Alterado em: ')
    atribuido                       = models.ForeignKey     (Utilizador, on_delete=models.PROTECT, verbose_name='Atribuido')
    numero_telefone                 = models.CharField      (max_length=15, verbose_name='Número do Telefone')
    numero_cartao                   = models.CharField      (max_length=15, blank=True, verbose_name='Número do Cartão')
    pin                             = models.CharField      (max_length=4, blank=True, verbose_name='PIN do Cartão')
    puk                             = models.CharField      (max_length=10, blank=True, verbose_name='PUK do Cartão')
    # Campo derivado de outro campo
    plano                           = models.ForeignKey     (PlanosTelemoveis, on_delete=models.PROTECT, verbose_name='Plano Associado')   

    class Meta:
        verbose_name_plural = ('Cartões Telemóveis')
    
    def __str__(self):
        return '{} | {} | {}' .format(self.atribuido, self.numero_cartao, self.plano)
    
# ---- Telemóveis ----------------------------------------------------------------------------#
class AparelhoTelemovel(models.Model):
     #  Nome Campo                          Tipo Model              Atributos    
    id                              = models.BigAutoField   (primary_key=True)
    registado                       = models.DateTimeField  (auto_now_add=True, verbose_name='Registado em:')
    editado                         = models.DateTimeField  (auto_now_add=True, verbose_name='Alterado em: ')
    telemovel                       = models.BooleanField   (verbose_name='Telemóvel', blank=True)
    # Campo derivado de outro campo
    nome_utilizador                 = models.ForeignKey     (Inventario, on_delete=models.PROTECT)
    numero_telefone                 = models.CharField      (max_length=20, verbose_name='Numero do Telemóvel', blank=True)
    # Campo derivado de outro campo
    cartao                          = models.ForeignKey     (CartaoTelemovel, on_delete=models.PROTECT)
    # Campo derivado de outro campo
    marca_esquipamento              = models.ForeignKey     (Marca, on_delete=models.PROTECT, verbose_name='Marca do Esquipamento')
    # Campo derivado de outro campo
    modelo_esquipamento             = models.ForeignKey     (Modelo, on_delete=models.PROTECT, verbose_name='Modelo do Equipamento')

    class Meta:
        verbose_name_plural = ('Aparelhos')

# ---- Criação de Utilizadores ----------------------------------------------------------------------------#

class CraicaoUtilizador(models.Model):
    #  Nome Campo                          Tipo Model              Atributos  
    id                                  = models.BigAutoField   (primary_key=True)
    registado                           = models.DateTimeField  (auto_now_add=True, verbose_name='Registado em:')
    editado                             = models.DateTimeField  (auto_now_add=True, verbose_name='Alterado em: ')
    solicitante                         = models.ForeignKey     (Utilizador, on_delete=models.PROTECT, verbose_name='Nome Solicitante')
    nome                                = models.CharField      (max_length=150, verbose_name='Nome Completo')
    setor                               = models.CharField      (max_length=20, choices=setor_choises, verbose_name='Departamento')
    email                               = models.EmailField     (verbose_name='E-mail Sugerido', blank=True)



#---- Fim do Model -------------------------------------------------------------#
