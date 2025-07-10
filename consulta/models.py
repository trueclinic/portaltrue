from django.db import models

# Create your models here.

# ---- Sinistrado ----------------------------------------------------------------------------#
class NomeSinistrado(models.Model):
#  Nome Campo          Tipo Model              Atributos    
    id                 = models.BigAutoField   (primary_key=True)
    registado          = models.DateTimeField  (auto_now_add=True, verbose_name='Registado em:')
    editado            = models.DateTimeField  (auto_now_add=True, verbose_name='Alterado em: ')
    nome_sinistrado    = models.CharField      (max_length=500, verbose_name='Nome do Sinistrado')
    numero_nif         = models.CharField      (max_length=50, verbose_name='Número do NIF', unique=True, )
    link_imagem        = models.CharField      (max_length=300, blank=True, verbose_name='Link das Imagens')

    class Meta:
        verbose_name_plural = ('Imagens dos Exames')

    def __str__(self):
        return '{}'.format(self.nome_sinistrado)

# ---- Registo dos Exames ----------------------------------------------------------------------------#
class RegistoExames(models.Model):
 #  Nome Campo          Tipo Model              Atributos
    id              = models.BigAutoField       (primary_key=True)
    registado       = models.DateTimeField      (auto_now_add=True, verbose_name='Registado em:')
    data_exame      = models.DateField          (verbose_name='Data do Exame')
    nome_exame      = models.ForeignKey         ('comum.NomeExame', on_delete=models.PROTECT, verbose_name='Nome do Exame')
    caixa           = models.IntegerField       (verbose_name='Caixa do Exame')
    nome_sinistrado = models.ForeignKey         (NomeSinistrado, on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = ('Registos dos Exames')

    def __str__(self):
        return '{}' .format(self.nome_exame)

#---- Fim do Model ------------------------------------------------------------#
