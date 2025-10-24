from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
import string
import pyotp
import qrcode
from io import BytesIO
import base64


class CodigoRecuperacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=6)
    criado_em = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)
    expira_em = models.DateTimeField()

    def __str__(self):
        return f"Código para {self.usuario.username}"

    @staticmethod
    def gerar_codigo():
        return ''.join(random.choices(string.digits, k=6))

    def esta_valido(self):
        return not self.usado and timezone.now() < self.expira_em

    class Meta:
        verbose_name = "Código de Recuperação"
        verbose_name_plural = "Códigos de Recuperação"
        ordering = ['-criado_em']


class UserProfile(models.Model):
    """Perfil do usuário com configurações de autenticação em duas etapas (2FA)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_2fa')
    two_fa_enabled = models.BooleanField(default=False)
    secret_key = models.CharField(max_length=255, blank=True, null=True)
    backup_codes = models.TextField(blank=True, null=True)  # Códigos separados por newline
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile 2FA de {self.user.username}"
    
    def generate_totp_secret(self):
        """Gera uma nova chave secreta TOTP"""
        self.secret_key = pyotp.random_base32()
        self.save()
        return self.secret_key
    
    def get_totp_uri(self):
        """Retorna a URI para gerar QR code"""
        if not self.secret_key:
            return None
        totp = pyotp.TOTP(self.secret_key)
        return totp.provisioning_uri(
            name=self.user.email or self.user.username,
            issuer_name='SGBooks'
        )
    
    def get_qr_code_image(self):
        """Gera imagem QR code em base64"""
        uri = self.get_totp_uri()
        if not uri:
            return None
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def verify_totp(self, token):
        """Verifica se o código TOTP é válido"""
        if not self.secret_key:
            return False
        
        try:
            totp = pyotp.TOTP(self.secret_key)
            # Permite uma variação de ±1 janela de tempo (±30 segundos)
            return totp.verify(token, valid_window=1)
        except:
            return False
    
    def generate_backup_codes(self, quantidade=10):
        """Gera códigos de backup para recuperação"""
        codes = []
        for _ in range(quantidade):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            codes.append(code)
        
        self.backup_codes = '\n'.join(codes)
        self.save()
        return codes
    
    def use_backup_code(self, code):
        """Usa um código de backup e remove da lista"""
        if not self.backup_codes:
            return False
        
        codes = self.backup_codes.strip().split('\n')
        
        if code in codes:
            codes.remove(code)
            self.backup_codes = '\n'.join(codes)
            self.save()
            return True
        
        return False
    
    class Meta:
        verbose_name = "Perfil 2FA"
        verbose_name_plural = "Perfis 2FA"