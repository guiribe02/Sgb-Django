"""
URLs do aplicativo sgb_usuarios
Todas as rotas aqui terão o prefixo /auth/
"""
from django.urls import path
from . import views

urlpatterns = [
    # ========================================
    # AUTENTICAÇÃO BÁSICA
    # ========================================
    path('cadastro/', views.cadastra_usuario, name='cadastro'),
    path('login/', views.loga_usuario, name='login'),
    path('logout/', views.logout_usuario, name='logout'),
    
    # ========================================
    # AUTENTICAÇÃO EM DUAS ETAPAS (2FA)
    # ========================================
    
    # ✅ MOVIDO DO urls.py PRINCIPAL
    # Verificação de código 2FA durante login
    path('2fa/', views.verify_2fa, name='verify_2fa'),
    
    # Configurar 2FA na conta
    path('setup-2fa/', views.setup_2fa, name='setup_2fa'),
    
    # Exibir códigos de backup
    path('backup-codes/', views.backup_codes_2fa, name='backup_codes_2fa'),
    
    # Desabilitar 2FA
    path('disable-2fa/', views.disable_2fa, name='disable_2fa'),
]