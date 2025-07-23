from ast import mod
from contextlib import ContextDecorator
from multiprocessing.reduction import send_handle
from xml.dom.expatbuilder import parseString
from django.db import models
from django.core.mail import send_mail

#-------------------------------- Choices -------------------------------------------------#
status_choices = [
        ('Ativo', 'Ativo'),
        ('Desativado', 'Desativado'),
    ]

status_outros_choices = [
        ('Ativo', 'Ativo'),
        ('Em Negociação', 'Em Negociação'),
        ('Desativado', 'Desativado'),
    ]

tipo_armazenamento_choices = [
    ('HD', 'HD'),
    ('SSD', 'SSD'),
]

tipo_IP_choices = [
    ('Fixo', 'Fixo'),
    ('Dinâmico', 'Dinâmico'),
]

versao_IP_choices = [
    ('IPV4', 'IPV4'),
    ('IPV6', 'IPV6'),
]

tipo_garantia_choices = [
    ('Balcão', 'Balcão'),
    ('On Site', 'On Site'),
]
tipo_licenca_choices = [
    ('Windows', 'Windows'),
    ('Office', 'Office'),
    ('Antivirus', 'Antivirus'), 
    ('Outros', 'Outros'),
]
certificado_digital_choices = [
    ('Sim', 'Sim'),
    ('Não', 'Não'),
]

local_trabalho_choices = [
    ('Escritório 1º Andar', 'Escritório 1º Andar'),
    ('Clínica', 'Clínica'),
    ('Sala Informática', 'Sala Informática')
]
#-------------------------------- FimChoices -------------------------------------------------#
    
# ---- Tipo do Exame --------------------------------------------------------------------#
class NomeExame(models.Model):
    id                              = models.BigAutoField   (primary_key=True)
    registado                       = models.DateTimeField  (auto_now_add=True, verbose_name='Registado em:')
    editado                         = models.DateTimeField  (auto_now_add=True, verbose_name='Alterado em: ')
    nome_exame                      = models.CharField      (max_length=100, verbose_name='Nome do Exame', unique=True)

    class Meta:
        verbose_name_plural = ('Nomes dos Exames')

    def __str__(self):
        return '{}'.format(self.nome_exame)
    


# ---- Utilizador ----------------------------------------------------------------------------#
class Utilizador(models.Model):
    id                              = models.BigAutoField   (primary_key=True)
    registado                       = models.DateTimeField  (auto_now_add=True, verbose_name='Registado em:')
    editado                         = models.DateTimeField  (auto_now_add=True, verbose_name='Alterado em: ')
    estatus_utilizador              = models.CharField      (max_length=10, choices=status_choices, default='em_uso', verbose_name='Estatus')
    nome_utilizador                 = models.CharField      (max_length=100, verbose_name='Nome Utilizador')
    local_trabalho                  = models.CharField      (max_length=15, verbose_name='Local de Trabalho')
    utilizador_plataforma           = models.CharField      (max_length=15, verbose_name='Utilizador Plataforma')
    departamento_utilizador         = models.ForeignKey     ('Departamento', on_delete=models.PROTECT, verbose_name='Nome Departamento', blank=True)

    class Meta:
        verbose_name_plural = ('Utilizadores TrueClinic')

    def __str__(self):
        return '{}' .format(self.nome_utilizador)
    

#---- Departamento ----------------------------------------------------------------------------#
class Departamento(models.Model):
    #  Nome Campo                           Tipo Model              Atributos
    id                              = models.BigAutoField   (primary_key=True)
    registado                       = models.DateTimeField  (auto_now_add=True, verbose_name='Registado em:')
    editado                         = models.DateTimeField  (auto_now_add=True, verbose_name='Alterado em: ')
    nome_departamento               = models.CharField      (max_length=20, unique=True)

    class Meta:
        verbose_name = ('Departamento')
        verbose_name_plural = ('Departamentos')

    def __str__(self):
        return '{}' .format(self.nome_departamento)
    
# ---- Emails TrueClinic --------------------------------------------------------------------#

class emailstrue(models.Model):
    id                              = models.BigAutoField   (primary_key=True)
    registado                       = models.DateTimeField  (auto_now_add=True, verbose_name='Registado em:')
    editado                         = models.DateTimeField  (auto_now=True, verbose_name='Alterado em: ')  # corrigido para auto_now
    estatus_email                   = models.CharField      (max_length=15, choices=status_choices, default='em_uso', verbose_name='Estatus')
    email                           = models.EmailField     (verbose_name='E-mail')
    palavra_passe                   = models.CharField      (max_length=20, verbose_name='Palavra-Passe Inicial do Email')
    tipo_licenca                    = models.ForeignKey     ('Licencas', on_delete=models.PROTECT, verbose_name='Tipo de Licença')
    caixa_compartilhada             = models.BooleanField   (default=False, verbose_name='Caixa Compartilhada?')

    class Meta:
        verbose_name_plural = ('Emails TrueClinic')

    def __str__(self):
        return '{} | {}'.format(self.email, self.tipo_licenca)

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Só envia no momento da criação
        super().save(*args, **kwargs)

        if is_new and self.email_pessoal:
            send_mail(
                subject='Palavra-passe do e-mail corporativo',
                message=f'Sua palavra-passe inicial para o e-mail {self.email} é: {self.palavra_passe}',
                from_email='nao-responda@trueclinic.pt',
                recipient_list=[self.email_pessoal],
                fail_silently=False,
            )

# ---- Licenças --------------------------------------------------------------------#
class Licencas(models.Model):
    id                              = models.BigAutoField   (primary_key=True)
    registado                       = models.DateTimeField  (auto_now_add=True, verbose_name='Registado em:')
    editado                         = models.DateTimeField  (auto_now_add=True, verbose_name='Alterado em: ')
    tipo_licenca                    = models.CharField      (max_length=100, verbose_name='Nome da Licença', unique=True)
    valor                           = models.DecimalField   (decimal_places=2, max_digits=9, verbose_name='Valor da Licença')
    fornecedor_licenca              = models.ForeignKey     ('Fornecedor', on_delete=models.PROTECT, verbose_name='Fornecedor')

    class Meta:
        verbose_name_plural = ('Licenças')

    def __str__(self):
        return '{}'.format(self.tipo_licenca)
    
#---- Fornecedor ----------------------------------------------------------------------------#
class Fornecedor(models.Model):
    id                              = models.BigAutoField   (primary_key=True)
    registado                       = models.DateTimeField  (auto_now_add=True, verbose_name='Registado em:')
    editado                         = models.DateTimeField  (auto_now_add=True, verbose_name='Alterado em: ')
    estatus_fornecedor              = models.CharField      (max_length=15, choices=status_outros_choices, default='em_uso', verbose_name='Estatus')
    nome_fornecedor                 = models.CharField      (max_length=100, verbose_name='Nome do Fornecedor', unique=True)
    nif                             = models.CharField      (max_length=11, verbose_name='NIF do Fornecedor', unique=True)
    telefone_contato                = models.CharField      (max_length=11, verbose_name='Telefone de Contato')
    email_fornecedor                = models.EmailField     (verbose_name='E-mail do Fornecedor')
    responsavel                     = models.CharField      (max_length=30, verbose_name='Nome do Responsável')
    contrato                        = models.BooleanField   (default=False, verbose_name='Tem contrato?')
    n_contrtato                     = models.CharField      (max_length=30, verbose_name='Nº Contrato', blank=True)

    class Meta:
        verbose_name = ('fornecedor')
        verbose_name_plural = ('Fornecedores')

    def __str__(self):
        return '{}' .format(self.nome_fornecedor)
    
#---- Marca ----------------------------------------------------------------------------#
class Marca(models.Model):
    id                              = models.BigAutoField   (primary_key=True)
    registado                       = models.DateTimeField  (auto_now_add=True, verbose_name='Registado em:')
    editado                         = models.DateTimeField  (auto_now_add=True, verbose_name='Alterado em: ')
    marca_equipamento               = models.CharField      (max_length=100, verbose_name='Marca do Equipamento', unique=True)

    class Meta:
        verbose_name_plural = ('Marca')

    def __str__(self):
        return '{}' .format(self.marca_equipamento)
    
# ---- Modelo Equipamento --------------------------------------------------------------------#
class Modelo(models.Model):
    id                              = models.BigAutoField   (primary_key=True)
    registado                       = models.DateTimeField  (auto_now_add=True, verbose_name='Registado em:')
    editado                         = models.DateTimeField  (auto_now_add=True, verbose_name='Alterado em: ')
    modelo_equipamento              = models.CharField      (max_length=100, verbose_name='Modelo do Equipamento', unique=True)

    class Meta:
        verbose_name_plural = ('Modelo')

    def __str__(self):
        return '{}' .format(self.modelo_equipamento)


# ---- Planos de Telemóveis --------------------------------------------------------------------#
class PlanosTelemoveis(models.Model):
    id                              = models.BigAutoField   (primary_key=True)
    registado                       = models.DateTimeField  (auto_now_add=True, verbose_name='Registado em:')
    editado                         = models.DateTimeField  (auto_now_add=True, verbose_name='Alterado em: ')
    plano                           = models.CharField      (max_length=20, verbose_name='Plano')
    valor                           = models.DecimalField   (decimal_places=2, max_digits=9, verbose_name='Valor do plano')

    class Meta:
        verbose_name_plural = ('Planos Telemóveis')

    def __str__(self):
        return '{}' .format(self.plano)


class LocalTrabalho(models.Model):
    nome = models.CharField(max_length=30)

    def __str__(self):
        return self.nome

#---- Nome do Equipamento ----------------------------------------------------------------------------#
class Nome_Equipamento_1(models.Model):
    #  Nome Campo                           Tipo Model              Atributos
    id                              = models.BigAutoField   (primary_key=True)
    registado                       = models.DateTimeField  (auto_now_add=True, verbose_name='Registado em:')
    editado                         = models.DateTimeField  (auto_now_add=True, verbose_name='Alterado em: ')
    nome_equipamento                = models.CharField      (max_length=20, unique=True, verbose_name='Nome do Esquipamento')

    class Meta:
        verbose_name = ('Nome do Equipamento')
        verbose_name_plural = ('Nomes dos Equipamentos')

    def __str__(self):
        return '{}' .format(self.nome_equipamento)
    
#---- Sistema Operacional ----------------------------------------------------------------------------#
class Nome_SO(models.Model):
    #  Nome Campo                           Tipo Model              Atributos
    id                              = models.BigAutoField   (primary_key=True)
    registado                       = models.DateTimeField  (auto_now_add=True, verbose_name='Registado em:')
    editado                         = models.DateTimeField  (auto_now_add=True, verbose_name='Alterado em: ')
    nome_sistema_operacional        = models.CharField      (max_length=20, unique=True, verbose_name='Nome do Sistema Operacional')

    class Meta:
        verbose_name = ('Nome do Sistema Operacional')
        verbose_name_plural = ('Nomes dos Sistemas Operacionais')

    def __str__(self):
        return '{}' .format(self.nome_sistema_operacional)