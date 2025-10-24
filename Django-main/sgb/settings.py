"""
Django settings for sgb project.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-jz%l)(q#^$t9j)m=c%c%ku7k60wpb^rt!zgfi@%t$)id6)j7wh'

DEBUG = True

ALLOWED_HOSTS = []

SITE_ID = 2

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sgb_livros',
    'sgb_usuarios',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google'
]

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email'
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'sgb_usuarios.middleware.Force2FAMiddleware',  # ✅ ADICIONADO: Middleware 2FA obrigatório
]

ROOT_URLCONF = 'sgb.urls'

# ========================================
# CONFIGURAÇÃO DE TEMPLATES
# ========================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'sgb_livros', 'templates'),
            os.path.join(BASE_DIR, 'sgb_usuarios', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sgb.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ========================================
# CONFIGURAÇÃO DE IDIOMA E TIMEZONE
# ========================================
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ========================================
# CONFIGURAÇÃO DE AUTENTICAÇÃO
# ========================================
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/livros/'
LOGOUT_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

SOCIALACCOUNT_LOGIN_ON_GET = True

# ========================================
# CONFIGURAÇÃO DE EMAIL - DESENVOLVIMENTO
# ========================================
# Para DESENVOLVIMENTO: mostra emails no console do terminal
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@sgbooks.com'

# Para PRODUÇÃO: descomente abaixo e use suas credenciais do Gmail
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'seu-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'sua-senha-de-app'  # Gere em myaccount.google.com/apppasswords
# DEFAULT_FROM_EMAIL = 'seu-email@gmail.com'

# ========================================
# CONFIGURAÇÃO DE PASSWORD RESET
# ========================================
# Validade do link de recuperação de senha (em segundos)
# Padrão: 259200 = 3 dias
PASSWORD_RESET_TIMEOUT = 259200  # 3 dias

# URLs para redirecionar após password reset
# (Já configurado em urls.py, mas pode ser sobrescrito aqui se necessário)

# ========================================
# CONFIGURAÇÃO DO DOMÍNIO (para emails)
# ========================================
if DEBUG:
    DOMAIN = 'localhost:8000'
    PROTOCOL = 'http'
else:
    # Altere para seu domínio em produção
    DOMAIN = 'seu-dominio.com'
    PROTOCOL = 'https'

# ========================================
# CONFIGURAÇÃO DE 2FA
# ========================================
TWO_FA_ENABLED = True  # Ativa 2FA obrigatório
TWO_FA_BACKUP_CODES_COUNT = 10  # Quantidade de códigos de backup
TWO_FA_MAX_ATTEMPTS = 5  # Máximo de tentativas de código inválido
TWO_FA_ISSUER_NAME = 'SGBooks'  # Nome da aplicação no app autenticador