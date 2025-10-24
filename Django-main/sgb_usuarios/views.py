from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from sgb_livros.models import Livro
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import CodigoRecuperacao, UserProfile


def cadastra_usuario(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        nome_usuario = request.POST['nome_usuario']
        nome = request.POST['nome']
        sobrenome = request.POST['sobrenome']
        email = request.POST['email']
        senha = request.POST['senha']

        usuario_existente = User.objects.filter(username=nome_usuario).first()
        
        if usuario_existente:
            messages.error(request, 'Usuário já existe! Tente outro nome de usuário.')
            return redirect('cadastro')
        else:
            usuario = User.objects.create_user(
                username=nome_usuario,
                first_name=nome,
                last_name=sobrenome,
                email=email,
                password=senha
            )
            usuario.save()
            
            # Criar perfil 2FA para o novo usuário
            UserProfile.objects.create(user=usuario)
            
            messages.success(request, f'Cadastro realizado com sucesso! Bem-vindo, {nome}!')
            return redirect('login')


def loga_usuario(request):
    """Login com suporte a 2FA"""
    # Se o usuário já estiver autenticado E a 2FA estiver ativada, mas não verificada, redireciona para a verificação.
    # Isso impede que o usuário veja a página de login novamente se ele já passou da autenticação inicial.
    if request.user.is_authenticated and hasattr(request.user, 'profile_2fa') and request.user.profile_2fa.two_fa_enabled and not request.session.get('two_factor_verified', False):
        return redirect('verify_2fa')
    # Se o usuário já estiver autenticado e a 2FA não for necessária ou já verificada, redireciona para a página inicial.
    elif request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    
    if request.method == "GET":
        return render(request, 'login.html') # Renderiza o template de login
    else:
        nome_usuario = request.POST['nome_usuario']
        senha = request.POST['senha']

        usuario = authenticate(request, username=nome_usuario, password=senha) # Adicionado 'request'

        if usuario:
            try:
                profile = usuario.profile_2fa
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=usuario)
            
            if profile.two_fa_enabled:
                # 2FA habilitado: armazenar user_id na sessão e redirecionar para verificação
                request.session['pre_2fa_user_id'] = usuario.id
                request.session['2fa_attempts'] = 0
                messages.info(request, 'Digite o código de autenticação do seu app.')
                return redirect('verify_2fa')
            else:
                # 2FA não habilitado: fazer login e redirecionar para a página principal
                login(request, usuario)
                messages.warning(request, 'Configure a verificação em 2 etapas para proteger sua conta.')
                return redirect(settings.LOGIN_REDIRECT_URL) # ALTERADO AQUI
        else:
            messages.error(request, 'Usuário ou senha inválidos!')
            return render(request, 'login.html') # Renderiza o template de login com erro


def verify_2fa(request):
    """Verifica o código 2FA"""
    user_id = request.session.get('pre_2fa_user_id')
    
    if not user_id:
        messages.error(request, 'Sessão inválida ou expirada. Faça login novamente.')
        return redirect('login')
    
    try:
        usuario = User.objects.get(id=user_id)
        profile = usuario.profile_2fa
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        messages.error(request, 'Erro ao verificar usuário.')
        return redirect('login')
    
    if request.method == "GET":
        return render(request, 'verificar_2fa.html', {'usuario': usuario.username})
    
    elif request.method == "POST":
        codigo = request.POST.get('code', '').strip()
        usar_backup = request.POST.get('usar_backup', False)
        
        if not codigo:
            messages.error(request, 'Por favor, digite o código.')
            return render(request, 'verificar_2fa.html', {'usuario': usuario.username})
        
        if len(codigo) != 6:
            messages.error(request, 'O código deve ter 6 dígitos.')
            return render(request, 'verificar_2fa.html', {'usuario': usuario.username})
        
        if not codigo.isdigit():
            messages.error(request, 'O código deve conter apenas números.')
            return render(request, 'verificar_2fa.html', {'usuario': usuario.username})
        
        if profile.verify_totp(codigo):
            login(request, usuario)
            request.session['two_factor_verified'] = True # Marca 2FA como verificada na sessão
            request.session.pop('pre_2fa_user_id', None)
            request.session.pop('2fa_attempts', None)
            
            messages.success(request, f'Bem-vindo de volta, {usuario.first_name}!')
            return redirect(settings.LOGIN_REDIRECT_URL) # Redireciona para a URL pós-login
        
        elif usar_backup and profile.use_backup_code(codigo):
            login(request, usuario)
            request.session['two_factor_verified'] = True # Marca 2FA como verificada na sessão
            request.session.pop('pre_2fa_user_id', None)
            request.session.pop('2fa_attempts', None)
            messages.warning(request, 'Login realizado com código de backup. Recomendamos gerar novos códigos.')
            return redirect(settings.LOGIN_REDIRECT_URL) # Redireciona para a URL pós-login
        
        else:
            attempts = request.session.get('2fa_attempts', 0) + 1
            request.session['2fa_attempts'] = attempts
            
            if attempts >= settings.TWO_FA_MAX_ATTEMPTS: # Usar a configuração do settings.py
                request.session.pop('pre_2fa_user_id', None)
                request.session.pop('2fa_attempts', None)
                messages.error(request, 'Muitas tentativas. Faça login novamente.')
                return redirect('login')
            
            messages.error(request, f'Código inválido. Tentativas restantes: {settings.TWO_FA_MAX_ATTEMPTS - attempts}')
            return render(request, 'verificar_2fa.html', {'usuario': usuario.username})


def logout_usuario(request):
    logout(request)
    request.session.pop('pre_2fa_user_id', None)
    request.session.pop('2fa_attempts', None)
    request.session.pop('two_factor_verified', None) # Limpa o status da 2FA na sessão
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('login')


# =====================================================
# FUNÇÕES DE CONFIGURAÇÃO DE 2FA
# =====================================================

@login_required
def setup_2fa(request):
    """Página para configurar 2FA"""
    
    try:
        profile = request.user.profile_2fa
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if profile.two_fa_enabled:
        messages.info(request, '2FA já está habilitado para sua conta.')
        return redirect(settings.LOGIN_REDIRECT_URL)
    
    if request.method == "GET":
        secret = profile.generate_totp_secret()
        qr_code = profile.get_qr_code_image()
        
        context = {
            'secret': secret,
            'qr_code': qr_code,
            'email': request.user.email,
            'user': request.user,
        }
        
        return render(request, 'usuarios/setup_2fa.html', context)
    
    elif request.method == "POST":
        codigo_verificacao = request.POST.get('verification_code', '').strip()
        
        if not codigo_verificacao or len(codigo_verificacao) != 6:
            messages.error('Código de verificação inválido.')
            return render(request, 'setup_2fa.html', {
                'secret': profile.secret_key,
                'qr_code': profile.get_qr_code_image(),
                'email': request.user.email,
                'user': request.user,
            })
        
        if profile.verify_totp(codigo_verificacao):
            profile.two_fa_enabled = True
            profile.save()
            
            backup_codes = profile.generate_backup_codes()
            
            messages.success(request, '2FA habilitado com sucesso!')

            return redirect('backup_codes_2fa')
        
        else:
            messages.error('Código de verificação inválido. Tente novamente.')
            return render(request, 'setup_2fa.html', {
                'secret': profile.secret_key,
                'qr_code': profile.get_qr_code_image(),
                'email': request.user.email,
                'user': request.user,
            })


@login_required
def backup_codes_2fa(request):
    """Exibe os códigos de backup"""
    
    try:
        profile = request.user.profile_2fa
    except UserProfile.DoesNotExist:
        messages.error(request, 'Perfil 2FA não encontrado.')
        return redirect('setup_2fa')
    
    if not profile.two_fa_enabled:
        messages.error(request, '2FA não está habilitado.')
        return redirect('setup_2fa')
    
    backup_codes = profile.backup_codes.strip().split('\n') if profile.backup_codes else []
    
    context = {
        'backup_codes': backup_codes,
        'total_codes': len(backup_codes),
    }
    
    return render(request, 'backup_codes_2fa.html', context)


@login_required  
def disable_2fa(request):
    """Desabilita 2FA"""
    
    try:
        profile = request.user.profile_2fa
    except UserProfile.DoesNotExist:
        messages.error(request, 'Perfil 2FA não encontrado.')
        return redirect('login')
    
    if request.method == "GET":
        return render(request, 'disable_2fa.html')
    
    elif request.method == "POST":
        senha = request.POST.get('password', '').strip()
        
        if not request.user.check_password(senha):
            messages.error('Senha incorreta.')
            return render('disable_2fa.html')
        
        profile.two_fa_enabled = False
        profile.secret_key = None
        profile.backup_codes = None
        profile.save()
        
        messages.success('2FA foi desabilitado.')
        return redirect(settings.LOGIN_REDIRECT_URL)

