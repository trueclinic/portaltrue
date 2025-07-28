from django.db import models
from comum.models import Marca, Modelo, emailstrue, PlanosTelemoveis, Fornecedor, Utilizador, Nome_Equipamento_1, Nome_SO
from cloudinary_storage.storage import MediaCloudinaryStorage


# Choices
STATUS_CHOICES = [
    ('em_uso', 'Em Uso'),
    ('desuso', 'Desuso'),
    ('descartado', 'Descartado'),
]

STATUSTELEMOVEL_CHOICES = [
    ('alocado', 'Alocado'),
    ('estoque', 'Estoque'),
    ('descartado', 'Descartado'),
]

# Inventário principal
class Inventario(models.Model):
    nome_utilizador = models.ForeignKey(Utilizador, on_delete=models.PROTECT, verbose_name='Nome do Utilizador')
    tag_da_porta = models.BooleanField(default=False, verbose_name='Tag da porta')
    numero_tag = models.CharField(max_length=50, blank=True, null=True, verbose_name='Número da TAG')
    email_pessoal = models.ForeignKey(emailstrue, on_delete=models.PROTECT, verbose_name='E-mail Pessoal', blank=True)
    registado = models.DateTimeField(auto_now_add=True)
    editado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Inventários'

    def __str__(self):
        return str(self.nome_utilizador)

# Email Compartilhado
class EmailCompartilhado(models.Model):
    email_compartilhado = models.ForeignKey(emailstrue, on_delete=models.PROTECT, verbose_name='Email')
    email_pessoal = models.ForeignKey(Inventario, on_delete=models.PROTECT)
    registado = models.DateTimeField(auto_now_add=True)
    editado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Emails Compartilhados'

    def __str__(self):
        return str(self.email_compartilhado)

# Equipamento do Inventário
class InventarioEquipamento(models.Model):
    estatus_equipamento = models.CharField(max_length=10, choices=STATUS_CHOICES, default='em_uso')
    nome_equipamento = models.ForeignKey(Nome_Equipamento_1, on_delete=models.PROTECT)
    atribuido_check = models.BooleanField(default=False, verbose_name='Atribuido')
    atribuido = models.ForeignKey(Utilizador, on_delete=models.PROTECT, blank=True, null=True)
    descricao_equipamento = models.TextField(blank=True)
    nome_rede = models.CharField(max_length=20, blank=True, null=True, unique=True)
    marca_esquipamento = models.ForeignKey(Marca, on_delete=models.PROTECT)
    modelo_esquipamento = models.ForeignKey(Modelo, on_delete=models.PROTECT)
    numero_serie = models.CharField(max_length=50, blank=True, null=True, unique=True)
    sistema_operacional = models.ForeignKey(Nome_SO, on_delete=models.PROTECT)
    memoria = models.CharField(max_length=20, blank=True)
    numero_ip = models.CharField(max_length=50, blank=True)
    mac = models.CharField(max_length=30, blank=True)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT)
    data_compra = models.DateField()
    data_garantia = models.DateField()
    tipo_garantia = models.CharField(max_length=10, blank=True)
    fatura = models.FileField(upload_to='faturas/', storage=MediaCloudinaryStorage(), blank=True)
    observacoes = models.TextField(blank=True)
    registado = models.DateTimeField(auto_now_add=True)
    editado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Inventário Equipamentos TrueClinic'

    def __str__(self):
        return f'{self.nome_equipamento} | {self.atribuido}'

# Relacionamento Inventário ↔ Equipamentos
class Equipamentos(models.Model):
    nome_equipamento = models.ForeignKey(InventarioEquipamento, on_delete=models.PROTECT)
    nome_utilizador = models.ForeignKey(Inventario, on_delete=models.PROTECT)
    registado = models.DateTimeField(auto_now_add=True)
    editado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Equipamentos'

    def __str__(self):
        return str(self.nome_equipamento)

# Cartão Telemóvel
class CartaoTelemovel(models.Model):
    atribuido = models.ForeignKey(Utilizador, on_delete=models.PROTECT)
    numero_telefone = models.CharField(max_length=15)
    numero_cartao = models.CharField(max_length=15, blank=True)
    pin = models.CharField(max_length=4, blank=True)
    puk = models.CharField(max_length=10, blank=True)
    plano = models.ForeignKey(PlanosTelemoveis, on_delete=models.PROTECT)
    registado = models.DateTimeField(auto_now_add=True)
    editado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Cartões Telemóveis'

    def __str__(self):
        return f'{self.atribuido} | {self.numero_cartao}'

# Aparelho Telemóvel
class AparelhoTelemovel(models.Model):
    estatus_telemovel = models.CharField(max_length=10, choices=STATUSTELEMOVEL_CHOICES, default='alocado')
    atribuido_1 = models.ForeignKey(Utilizador, on_delete=models.PROTECT, blank=True, null=True)
    numero_telefone = models.CharField(max_length=20, blank=True, null=True)
    cartao = models.ForeignKey(CartaoTelemovel, on_delete=models.PROTECT, blank=True, null=True)
    marca_esquipamento = models.ForeignKey(Marca, on_delete=models.PROTECT)
    modelo_esquipamento = models.ForeignKey(Modelo, on_delete=models.PROTECT)
    registado = models.DateTimeField(auto_now_add=True)
    editado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Aparelhos'

    def __str__(self):
        return f'{self.modelo_esquipamento} | {self.atribuido_1 or "Sem Utilizador"}'
    
