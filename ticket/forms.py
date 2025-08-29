from django import forms
from django.contrib.auth.models import User
from .models import Ticket, TicketComment, TicketAttachment


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['titulo', 'descricao']  # prioridade só por staff


class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['status', 'atribuido_para', 'prioridade', 'reporter_nome', 'reporter_email']
    atribuido_para = forms.ModelChoiceField(queryset=User.objects.all(), required=False)


class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ['mensagem']
        widgets = {
            'mensagem': forms.Textarea(attrs={'rows': 3}),
        }


class TicketAttachmentForm(forms.ModelForm):
    class Meta:
        model = TicketAttachment
        fields = ['ficheiro']



