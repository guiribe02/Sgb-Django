from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Comentado para evitar redirecionamento indesejado com 2FA
    # path('', lambda request: redirect('login'), name='home'),
    path('', lambda request: redirect('auth/login/'), name='home'), # Nova rota para a home, redirecionando para o login
    
    path('livros/', include('sgb_livros.urls')),
    
    # ✅ Rotas de autenticação (inclui login, cadastro E 2FA)
    path('auth/', include('sgb_usuarios.urls')),
    
    # ✅ AllAuth (Google login)
    path('accounts/', include('allauth.urls')),
    
    # ========================================
    # Sistema de Recuperação de Senha (Django Built-in)
    # ========================================
    
    # 1. Página para digitar o email
    path('recuperar-senha/',
         auth_views.PasswordResetView.as_view(
             template_name='usuarios/password_reset_form.html',
             email_template_name='usuarios/password_reset_email.html',
             subject_template_name='usuarios/password_reset_subject.txt',
             success_url='/email-enviado/'
         ),
         name='password_reset'),
    
    # 2. Confirmação de que o email foi enviado
    path('email-enviado/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='usuarios/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    # 3. Página para criar nova senha (link do email)
    path('redefinir/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='usuarios/password_reset_confirm.html',
             success_url='/senha-alterada/'
         ),
         name='password_reset_confirm'),
    
    # 4. Confirmação final
    path('senha-alterada/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='usuarios/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
