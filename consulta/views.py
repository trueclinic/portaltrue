from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from openpyxl import Workbook
import csv
from django.db.models import Q
from .models import RegistoExames, NomeSinistrado
from django import forms
from django.forms import inlineformset_factory
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta


def _query_exames(request):
    qs = RegistoExames.objects.select_related('nome_exame', 'nome_sinistrado').order_by('-data_exame', '-id')

    f_nome = (request.GET.get('nome') or '').strip()
    f_nif = (request.GET.get('nif') or '').strip()
    f_data = (request.GET.get('data') or '').strip()
    f_range = (request.GET.get('range') or '').strip()

    if f_nome:
        qs = qs.filter(Q(nome_sinistrado__nome_sinistrado__icontains=f_nome) | Q(nome_exame__nome_exame__icontains=f_nome))
    if f_nif:
        qs = qs.filter(nome_sinistrado__numero_nif__icontains=f_nif)
    if f_data:
        qs = qs.filter(data_exame=f_data)
    if f_range == 'week':
        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())
        qs = qs.filter(data_exame__gte=week_start, data_exame__lte=today)

    return qs


@login_required
def lista_exames(request):
    qs = _query_exames(request)

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    # KPIs gerais de exames
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    kpi_exames = {
        'hoje': RegistoExames.objects.filter(registado__date=today).count(),
        'semana': RegistoExames.objects.filter(registado__date__gte=week_start).count(),
        'total': RegistoExames.objects.count(),
    }

    return render(request, 'consulta/lista.html', {
        'exames': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'f_nome': (request.GET.get('nome') or '').strip(),
        'f_nif': (request.GET.get('nif') or '').strip(),
        'f_data': (request.GET.get('data') or '').strip(),
        'kpi_exames': kpi_exames,
        'today': today,
    })


@login_required
def detalhe_exame(request, exame_id: int):
    exame = get_object_or_404(RegistoExames.objects.select_related('nome_exame', 'nome_sinistrado'), id=exame_id)
    relacionados = RegistoExames.objects.select_related('nome_exame').filter(
        nome_sinistrado=exame.nome_sinistrado
    ).exclude(id=exame.id).order_by('-data_exame')[:8]
    return render(request, 'consulta/detalhe.html', {'exame': exame, 'relacionados': relacionados})


class NomeSinistradoForm(forms.ModelForm):
    class Meta:
        model = NomeSinistrado
        fields = ['nome_sinistrado', 'numero_nif', 'link_imagem']


RegistoExamesFormSet = inlineformset_factory(
    parent_model=NomeSinistrado,
    model=RegistoExames,
    fields=['data_exame', 'nome_exame', 'caixa'],
    extra=1,
    can_delete=True
)


@login_required
def criar_exame(request):
    if not request.user.is_staff:
        return render(request, '403.html', status=403)
    if request.method == 'POST':
        sin_form = NomeSinistradoForm(request.POST)
        if sin_form.is_valid():
            with transaction.atomic():
                sinistrado = sin_form.save()
                formset = RegistoExamesFormSet(request.POST, instance=sinistrado, prefix='exames')
                if formset.is_valid():
                    exames_salvos = formset.save()
                    messages.success(request, f"{len(exames_salvos)} registo(s) de exame gravado(s) para {sinistrado.nome_sinistrado}.")
                    return redirect('consulta:lista')
                else:
                    # Se inválido, remover registro criado para não sujar base
                    sinistrado.delete()
                    return render(request, 'consulta/criar.html', {
                        'sin_form': sin_form,
                        'formset': formset,
                    })
        else:
            # Recriar formset vazio para re-renderização
            formset = RegistoExamesFormSet(request.POST, prefix='exames')
            return render(request, 'consulta/criar.html', {
                'sin_form': sin_form,
                'formset': formset,
            })
    else:
        sin_form = NomeSinistradoForm()
        formset = RegistoExamesFormSet(prefix='exames')
    return render(request, 'consulta/criar.html', {'sin_form': sin_form, 'formset': formset})


@login_required
def exportar_exames_csv(request):
    qs = _query_exames(request)
    response = render(request, 'consulta/lista.html')  # placeholder to get response object
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="exames.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Data', 'Exame', 'Sinistrado', 'NIF', 'Caixa'])
    for e in qs:
        writer.writerow([e.id, e.data_exame, getattr(e.nome_exame, 'nome_exame', ''), e.nome_sinistrado.nome_sinistrado, e.nome_sinistrado.numero_nif, e.caixa])
    return response


@login_required
def exportar_exames_xlsx(request):
    qs = _query_exames(request)
    wb = Workbook()
    ws = wb.active
    ws.title = 'Exames'
    ws.append(['ID', 'Data', 'Exame', 'Sinistrado', 'NIF', 'Caixa'])
    for e in qs:
        ws.append([e.id, str(e.data_exame), getattr(e.nome_exame, 'nome_exame', ''), e.nome_sinistrado.nome_sinistrado, e.nome_sinistrado.numero_nif, e.caixa])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="exames.xlsx"'
    wb.save(response)
    return response
