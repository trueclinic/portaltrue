from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from ticket.models import Ticket
from consulta.models import RegistoExames

# Create your views here.

def home(request):
    # Se já estiver autenticado, não mostrar login
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    # Ao chegar via GET (ex.: após logout), limpe mensagens antigas de outras páginas
    if request.method == 'GET':
        from django.contrib import messages as dj_messages
        storage = dj_messages.get_messages(request)
        for _ in storage:
            # Consumir sem renderizar, para não mostrar mensagens de outras páginas
            pass
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            messages.error(request, 'Utilizador não encontrado para este email.')
            return render(request, 'autenticador/home.html')
        user_auth = authenticate(request, username=user.username, password=password)
        if user_auth is None:
            messages.error(request, 'Credenciais inválidas.')
            return render(request, 'autenticador/home.html')
        code = get_random_string(length=6, allowed_chars='0123456789')
        request.session['mfa_user_id'] = user_auth.id
        request.session['mfa_code'] = code
        request.session['mfa_expires'] = __import__('time').time() + 120  # 2 minutos
        request.session['mfa_attempts'] = 0
        # Enviar código (em dev pode falhar SMTP; ok mostrar em /debug/mfa/)
        try:
            send_mail(
                subject='Seu código de verificação',
                message=f'Seu código é: {code}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:
            pass
        return redirect('autenticador:mfa_verificar')
    return render(request, "autenticador/home.html")


def mfa_verificar(request):
    # Página de verificação em modal (renderizamos template com js)
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        session_code = request.session.get('mfa_code')
        user_id = request.session.get('mfa_user_id')
        expires = request.session.get('mfa_expires')
        attempts = request.session.get('mfa_attempts', 0)
        if not (session_code and user_id):
            messages.error(request, 'Sessão expirada. Faça login novamente.')
            return redirect('autenticador:home')
        import time
        if expires and time.time() > float(expires):
            messages.error(request, 'Código expirado. Reenvie para continuar.')
            return redirect('autenticador:mfa_verificar')
        if attempts >= 5:
            messages.error(request, 'Muitas tentativas. Inicie sessão novamente.')
            for k in ['mfa_user_id','mfa_code','mfa_expires','mfa_attempts']:
                if k in request.session:
                    del request.session[k]
            return redirect('autenticador:home')
        if code != session_code:
            request.session['mfa_attempts'] = attempts + 1
            messages.error(request, f'Código inválido. Tentativas: {attempts+1}/5')
            return redirect('autenticador:mfa_verificar')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, 'Utilizador não encontrado.')
            return redirect('autenticador:home')
        login(request, user)
        for k in ['mfa_user_id', 'mfa_code', 'mfa_expires', 'mfa_attempts']:
            if k in request.session:
                del request.session[k]
        return redirect('/dashboard/')
    import time
    code = request.session.get('mfa_code')
    expires = request.session.get('mfa_expires')
    seconds_left = 120
    if expires:
        try:
            seconds_left = max(0, int(float(expires) - time.time()))
        except Exception:
            seconds_left = 120
    return render(request, 'autenticador/mfa_modal.html', {
        'debug': settings.DEBUG,
        'debug_code': code if settings.DEBUG else None,
        'seconds_left': seconds_left,
    })


def mfa_reenviar(request):
    user_id = request.session.get('mfa_user_id')
    if not user_id:
        return redirect('autenticador:home')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('autenticador:home')
    code = get_random_string(length=6, allowed_chars='0123456789')
    request.session['mfa_code'] = code
    request.session['mfa_expires'] = __import__('time').time() + 120
    request.session['mfa_attempts'] = 0
    try:
        send_mail(
            subject='Seu código de verificação',
            message=f'Seu código é: {code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception:
        pass
    messages.success(request, 'Código reenviado.')
    return redirect('autenticador:mfa_verificar')


def debug_mfa(request):
    # Exibe o código atual em ambiente de desenvolvimento
    code = request.session.get('mfa_code')
    return render(request, 'autenticador/debug_mfa.html', {'code': code})


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def dashboard(request):
    qs = Ticket.objects.all() if request.user.is_staff else Ticket.objects.filter(criado_por=request.user)
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
    recentes = list(qs.order_by('-criado_em')[:5])
    context = {
        'status_counts': status_counts,
        'prioridade_counts': prioridade_counts,
        'recentes': recentes,
        'total': qs.count(),
        'tickets_abertos': status_counts.get('aberto', 0),
        'exames_total': RegistoExames.objects.count(),
    }
    return render(request, 'dashboard.html', context)


@staff_member_required
def admin_send_test_email(request):
    """Endpoint protegido no admin para envio de e-mail de teste.
    Use parâmetro opcional "to" em querystring para definir o destinatário.
    Ex.: /admin/enviar-email-teste/?to=alguem@dominio.pt
    """
    recipient = request.GET.get('to') or settings.EMAIL_HOST_USER
    try:
        send_mail(
            subject='[PortalTrue] Teste via Admin',
            message='Envio de teste de e-mail disparado pelo endpoint do admin.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        messages.success(request, f'E-mail de teste enviado para {recipient}.')
    except Exception as exc:
        messages.error(request, f'Falha ao enviar e-mail: {type(exc).__name__}: {exc}')
    return redirect('/admin/')