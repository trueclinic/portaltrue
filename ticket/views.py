from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
import csv
from openpyxl import Workbook
from .models import Ticket, TicketAttachment
from .forms import TicketForm, TicketUpdateForm, TicketCommentForm, TicketAttachmentForm


@login_required
def lista_tickets(request):
    if request.user.is_staff:
        qs = Ticket.objects.all()
    else:
        # Inclui tickets criados pelo utilizador OU reportados pelo email dele (ex.: abertos via e‑mail)
        user_email = (request.user.email or '').strip()
        qs = Ticket.objects.filter(Q(criado_por=request.user) | Q(reporter_email__iexact=user_email))
    status = request.GET.get('status') or ''
    prioridade = request.GET.get('prioridade') or ''
    assigned = request.GET.get('assigned') or ''
    q = request.GET.get('q') or ''
    if status:
        qs = qs.filter(status=status)
    if prioridade:
        qs = qs.filter(prioridade=prioridade)
    if request.user.is_staff and assigned:
        if assigned == 'me':
            qs = qs.filter(atribuido_para=request.user)
        elif assigned == 'unassigned':
            qs = qs.filter(atribuido_para__isnull=True)
    if q:
        qs = qs.filter(Q(titulo__icontains=q) | Q(descricao__icontains=q))
    qs = qs.order_by('-criado_em')
    paginator = Paginator(qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    status_counts = {
        'aberto': qs.filter(status='aberto').count(),
        'em_andamento': qs.filter(status='em_andamento').count(),
        'resolvido': qs.filter(status='resolvido').count(),
        'fechado': qs.filter(status='fechado').count(),
    }
    prioridade_counts = {
        'baixa': qs.filter(prioridade='baixa').count(),
        'media': qs.filter(prioridade='media').count(),
        'alta': qs.filter(prioridade='alta').count(),
    }
    return render(request, 'ticket/lista.html', {
        'tickets': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'f_status': status,
        'f_prioridade': prioridade,
        'f_q': q,
        'assigned': assigned,
        'status_counts': status_counts,
        'prioridade_counts': prioridade_counts,
    })


@login_required
def _query_tickets(request):
    qs = Ticket.objects.all() if request.user.is_staff else Ticket.objects.filter(criado_por=request.user)
    status = request.GET.get('status') or ''
    prioridade = request.GET.get('prioridade') or ''
    assigned = request.GET.get('assigned') or ''
    q = request.GET.get('q') or ''
    if status:
        qs = qs.filter(status=status)
    if prioridade:
        qs = qs.filter(prioridade=prioridade)
    if request.user.is_staff and assigned:
        if assigned == 'me':
            qs = qs.filter(atribuido_para=request.user)
        elif assigned == 'unassigned':
            qs = qs.filter(atribuido_para__isnull=True)
    if q:
        qs = qs.filter(Q(titulo__icontains=q) | Q(descricao__icontains=q))
    return qs.order_by('-criado_em')


@login_required
def exportar_tickets_csv(request):
    tickets = _query_tickets(request)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tickets.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Título', 'Prioridade', 'Status', 'Criado por', 'Atribuído para', 'Criado em'])
    for t in tickets:
        writer.writerow([t.id, t.titulo, t.get_prioridade_display(), t.get_status_display(), t.criado_por.username, (t.atribuido_para.username if t.atribuido_para else ''), t.criado_em])
    return response


@login_required
def exportar_tickets_xlsx(request):
    tickets = _query_tickets(request)
    wb = Workbook()
    ws = wb.active
    ws.title = 'Tickets'
    ws.append(['ID', 'Título', 'Prioridade', 'Status', 'Criado por', 'Atribuído para', 'Criado em'])
    for t in tickets:
        ws.append([t.id, t.titulo, t.get_prioridade_display(), t.get_status_display(), t.criado_por.username, (t.atribuido_para.username if t.atribuido_para else ''), str(t.criado_em)])
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="tickets.xlsx"'
    wb.save(response)
    return response


@login_required
def criar_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.criado_por = request.user
            ticket.reporter_nome = request.user.get_full_name() or request.user.username
            ticket.reporter_email = request.user.email
            ticket.save()
            # Se vier um anexo na criação, salvar ligado ao ticket
            if request.FILES.get('ficheiro'):
                a = TicketAttachment(ticket=ticket, ficheiro=request.FILES['ficheiro'], enviado_por=request.user)
                a.save()
            return redirect(reverse('ticket:detalhe', args=[ticket.id]))
    else:
        form = TicketForm()
    return render(request, 'ticket/criar.html', {'form': form})


@login_required
def detalhe_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if not request.user.is_staff and ticket.criado_por != request.user:
        return redirect('ticket:lista')
    if request.method == 'POST':
        if 'mensagem' in request.POST:
            c_form = TicketCommentForm(request.POST)
            if c_form.is_valid():
                c = c_form.save(commit=False)
                c.ticket = ticket
                c.autor = request.user
                c.save()
                messages.success(request, 'Comentário adicionado.')
                return redirect('ticket:detalhe', ticket_id=ticket.id)
        elif 'status' in request.POST or 'atribuido_para' in request.POST or 'prioridade' in request.POST:
            if not request.user.is_staff:
                messages.error(request, 'Apenas equipa pode atualizar o ticket.')
                return redirect('ticket:detalhe', ticket_id=ticket.id)
            u_form = TicketUpdateForm(request.POST, instance=ticket)
            if u_form.is_valid():
                u_form.save()
                messages.success(request, 'Ticket atualizado.')
                return redirect('ticket:detalhe', ticket_id=ticket.id)
        elif 'ficheiro' in request.FILES:
            a_form = TicketAttachmentForm(request.POST, request.FILES)
            if a_form.is_valid():
                a = a_form.save(commit=False)
                a.ticket = ticket
                a.enviado_por = request.user
                a.save()
                messages.success(request, 'Anexo enviado.')
                return redirect('ticket:detalhe', ticket_id=ticket.id)
    c_form = TicketCommentForm()
    u_form = TicketUpdateForm(instance=ticket)
    a_form = TicketAttachmentForm()
    return render(request, 'ticket/detalhe.html', {'ticket': ticket, 'c_form': c_form, 'u_form': u_form, 'a_form': a_form})
