from django import forms
from .models import InventarioEquipamento

class InventarioEquipamentoForm(forms.ModelForm):
    memoria_opcoes = [
        ('4MB', '4MB'),
        ('8MB', '8MB'),
        ('16MB', '16MB'),
        ('32MB', '32MB'),
        ('outros', 'Outros'),
    ]

    tipo_ip_opcoes = [
        ('dinamico', 'IP Dinâmico'),
        ('fixo', 'IP Fixo'),
    ]

    memoria_select = forms.ChoiceField(choices=memoria_opcoes, required=False, label='Memória')
    tipo_ip_select = forms.ChoiceField(choices=tipo_ip_opcoes, required=False, label='Tipo de IP')

    atribuido_check = forms.BooleanField(required=False, label='Atribuído?')

    class Meta:
        model = InventarioEquipamento
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Memória
        if self.instance and self.instance.memoria:
            if self.instance.memoria in dict(self.memoria_opcoes):
                self.fields['memoria_select'].initial = self.instance.memoria
            else:
                self.fields['memoria_select'].initial = 'outros'
                self.fields['memoria'].initial = self.instance.memoria

        # IP
        if self.instance and self.instance.numero_ip:
            self.fields['tipo_ip_select'].initial = 'fixo'
        else:
            self.fields['tipo_ip_select'].initial = 'dinamico'

        # Atribuido check
        if self.instance and self.instance.atribuido:
            self.fields['atribuido_check'].initial = True
        else:
            self.fields['atribuido_check'].initial = False

        # Se não atribuído, opcionalmente desabilitar o campo atribuido
        if not self.fields['atribuido_check'].initial:
            self.fields['atribuido'].widget.attrs['style'] = 'display:none;'
