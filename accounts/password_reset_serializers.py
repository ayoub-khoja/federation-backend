"""
Sérialiseurs pour la réinitialisation de mot de passe
"""
from rest_framework import serializers
from .models import Arbitre, Commissaire, Admin, PasswordResetToken

class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer pour demander une réinitialisation de mot de passe"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validation de l'email"""
        if not value:
            raise serializers.ValidationError("L'adresse email est requise.")
        
        # Vérifier que l'email existe dans la base de données
        user = None
        user_type = None
        
        # Chercher dans Arbitre
        try:
            user = Arbitre.objects.get(email=value, is_active=True)
            user_type = 'arbitre'
        except Arbitre.DoesNotExist:
            pass
        
        # Chercher dans Commissaire
        if not user:
            try:
                user = Commissaire.objects.get(email=value, is_active=True)
                user_type = 'commissaire'
            except Commissaire.DoesNotExist:
                pass
        
        # Chercher dans Admin
        if not user:
            try:
                user = Admin.objects.get(email=value, is_active=True)
                user_type = 'admin'
            except Admin.DoesNotExist:
                pass
        
        if not user:
            raise serializers.ValidationError(
                "Aucun compte actif trouvé avec cette adresse email."
            )
        
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer pour confirmer la réinitialisation de mot de passe"""
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Validation des données de réinitialisation"""
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if new_password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Les mots de passe ne correspondent pas.'
            })
        
        # Validation de la force du mot de passe
        if len(new_password) < 8:
            raise serializers.ValidationError({
                'new_password': 'Le mot de passe doit contenir au moins 8 caractères.'
            })
        
        if not any(c.isdigit() for c in new_password):
            raise serializers.ValidationError({
                'new_password': 'Le mot de passe doit contenir au moins un chiffre.'
            })
        
        if not any(c.isalpha() for c in new_password):
            raise serializers.ValidationError({
                'new_password': 'Le mot de passe doit contenir au moins une lettre.'
            })
        
        return data
    
    def validate_token(self, value):
        """Validation du token"""
        token_obj = PasswordResetToken.get_valid_token(value)
        if not token_obj:
            raise serializers.ValidationError(
                "Token invalide ou expiré. Veuillez demander un nouveau lien de réinitialisation."
            )
        
        return value

class PasswordResetOTPVerifySerializer(serializers.Serializer):
    """Serializer pour vérifier le code OTP"""
    token = serializers.CharField()
    otp_code = serializers.CharField(max_length=6, min_length=6)
    
    def validate(self, data):
        """Validation du code OTP"""
        token = data.get('token')
        otp_code = data.get('otp_code')
        
        # Vérifier que le code OTP contient seulement des chiffres
        if not otp_code.isdigit():
            raise serializers.ValidationError({
                'otp_code': 'Le code OTP doit contenir seulement des chiffres.'
            })
        
        # Vérifier que le code OTP fait exactement 6 chiffres
        if len(otp_code) != 6:
            raise serializers.ValidationError({
                'otp_code': 'Le code OTP doit contenir exactement 6 chiffres.'
            })
        
        return data
    
    def validate_token(self, value):
        """Validation du token"""
        token_obj = PasswordResetToken.get_valid_otp_token(value)
        if not token_obj:
            raise serializers.ValidationError(
                "Token invalide, expiré ou OTP déjà vérifié. Veuillez demander un nouveau lien de réinitialisation."
            )
        
        return value

class PasswordResetConfirmWithOTPSerializer(serializers.Serializer):
    """Serializer pour confirmer la réinitialisation avec OTP vérifié"""
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Validation des données de réinitialisation"""
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if new_password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Les mots de passe ne correspondent pas.'
            })
        
        # Validation de la force du mot de passe
        if len(new_password) < 8:
            raise serializers.ValidationError({
                'new_password': 'Le mot de passe doit contenir au moins 8 caractères.'
            })
        
        if not any(c.isdigit() for c in new_password):
            raise serializers.ValidationError({
                'new_password': 'Le mot de passe doit contenir au moins un chiffre.'
            })
        
        if not any(c.isalpha() for c in new_password):
            raise serializers.ValidationError({
                'new_password': 'Le mot de passe doit contenir au moins une lettre.'
            })
        
        return data
    
    def validate_token(self, value):
        """Validation du token avec OTP vérifié"""
        token_obj = PasswordResetToken.get_valid_token(value)
        if not token_obj:
            raise serializers.ValidationError(
                "Token invalide ou expiré. Veuillez demander un nouveau lien de réinitialisation."
            )
        
        if not token_obj.otp_verified:
            raise serializers.ValidationError(
                "Le code OTP n'a pas été vérifié. Veuillez d'abord vérifier votre code OTP."
            )
        
        return value
