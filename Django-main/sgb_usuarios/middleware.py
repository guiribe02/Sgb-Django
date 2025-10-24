"""
Middleware para forçar autenticação em duas etapas (2FA)
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser
from sgb_usuarios.models import UserProfile


class Force2FAMiddleware:
    """
    Middleware que força o usuário autenticado a configurar 2FA
    antes de acessar qualquer página protegida.
    
    Páginas permitidas sem 2FA:
    - Login
    - Logout
    - Cadastro
    - Verificação 2FA
    - Setup 2FA
    - Backup codes 2FA
    - Disable 2FA
    - Recuperação de senha (todas as etapas)
    """
    
    # URLs que NÃO requerem 2FA verificado
    URLS_PERMITIDAS = [
        '/auth/login/',  # ✅ CORRIGIDO
        '/auth/logout/',  # ✅ CORRIGIDO
        '/auth/cadastro/',  # ✅ CORRIGIDO
        '/auth/2fa/',  # Verificação 2FA
        '/auth/setup-2fa/',  # ✅ CORRIGIDO
        '/auth/backup-codes/',  # ✅ CORRIGIDO
        '/auth/disable-2fa/',  # ✅ CORRIGIDO
        '/recuperar-senha/',
        '/email-enviado/',
        '/redefinir/',
        '/senha-alterada/',
        '/accounts/',  # AllAuth
        '/admin/',  # Django Admin
        '/static/',  # Arquivos estáticos
        '/media/',   # Arquivos de mídia
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Intercepta cada request antes da view ser executada
        """
        
        # ✅ CORREÇÃO 1: Se o usuário NÃO está autenticado, ou se a URL está na lista de permitidas, deixa passar.
        # Isso garante que a página de login e outras rotas públicas funcionem sem 2FA.
        if not request.user.is_authenticated or isinstance(request.user, AnonymousUser) or self._url_esta_permitida(request.path):
            return None
        

        
        # ✅ CORREÇÃO 3: Se o usuário está autenticado e a 2FA está habilitada, mas ainda não verificada nesta sessão,
        # e a URL atual não é a de verificação 2FA, redireciona para a página de 2FA.
        if hasattr(request.user, 'profile_2fa') and request.user.profile_2fa.two_fa_enabled and not request.session.get('two_factor_verified', False):
            if request.path != reverse('verify_2fa'):
                return redirect('verify_2fa')
        
        # Verificar se o usuário tem 2FA habilitado
        try:
            profile = request.user.profile_2fa
        except UserProfile.DoesNotExist:
            # Se não tiver profile, criar um
            profile = UserProfile.objects.create(user=request.user)
        
        # ✅ CORREÇÃO 4: Se 2FA não está habilitado e a URL atual não é a de setup 2FA, redirecionar para setup.
        if not request.user.profile_2fa.two_fa_enabled:
            if request.path != reverse('setup_2fa'):
                return redirect('setup_2fa')
        
        # Se chegou aqui, usuário está autenticado E tem 2FA configurado
        return None
    
    def _url_esta_permitida(self, path):
        """
        Verifica se a URL está na lista de URLs permitidas
        """
        for url_permitida in self.URLS_PERMITIDAS:
            if path.startswith(url_permitida):
                return True
        
        return False