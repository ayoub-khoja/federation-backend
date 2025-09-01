"""
Système d'authentification personnalisé pour gérer les trois types d'utilisateurs
"""
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .models import Arbitre, Commissaire, Admin

class MultiUserBackend(BaseBackend):
    """
    Backend d'authentification personnalisé qui permet de se connecter
    avec n'importe lequel des trois types d'utilisateurs
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authentifie un utilisateur en essayant de le trouver dans les trois modèles
        """
        if username is None or password is None:
            return None
        
        # Essayer de trouver l'utilisateur dans Arbitre
        try:
            user = Arbitre.objects.get(phone_number=username)
            if user.check_password(password) and user.is_active:
                return user
        except Arbitre.DoesNotExist:
            pass
        
        # Essayer de trouver l'utilisateur dans Commissaire
        try:
            user = Commissaire.objects.get(phone_number=username)
            if user.check_password(password) and user.is_active:
                return user
        except Commissaire.DoesNotExist:
            pass
        
        # Essayer de trouver l'utilisateur dans Admin
        try:
            user = Admin.objects.get(phone_number=username)
            if user.check_password(password) and user.is_active:
                return user
        except Admin.DoesNotExist:
            pass
        
        return None
    
    def get_user(self, user_id):
        """
        Récupère un utilisateur par son ID en cherchant dans les trois modèles
        """
        # Essayer de trouver l'utilisateur dans Arbitre
        try:
            return Arbitre.objects.get(pk=user_id)
        except Arbitre.DoesNotExist:
            pass
        
        # Essayer de trouver l'utilisateur dans Commissaire
        try:
            return Commissaire.objects.get(pk=user_id)
        except Commissaire.DoesNotExist:
            pass
        
        # Essayer de trouver l'utilisateur dans Admin
        try:
            return Admin.objects.get(pk=user_id)
        except Admin.DoesNotExist:
            pass
        
        return None

def get_user_by_phone(phone_number):
    """
    Fonction utilitaire pour récupérer un utilisateur par son numéro de téléphone
    """
    # Essayer de trouver l'utilisateur dans Arbitre
    try:
        return Arbitre.objects.get(phone_number=phone_number)
    except Arbitre.DoesNotExist:
        pass
    
    # Essayer de trouver l'utilisateur dans Commissaire
    try:
        return Commissaire.objects.get(phone_number=phone_number)
    except Commissaire.DoesNotExist:
        pass
    
    # Essayer de trouver l'utilisateur dans Admin
    try:
        return Admin.objects.get(phone_number=phone_number)
    except Admin.DoesNotExist:
        pass
    
    return None

def get_user_type(user):
    """
    Détermine le type d'utilisateur d'un objet utilisateur
    """
    if isinstance(user, Arbitre):
        return 'arbitre'
    elif isinstance(user, Commissaire):
        return 'commissaire'
    elif isinstance(user, Admin):
        return 'admin'
    else:
        return 'unknown'

# ============================================================================
# AUTHENTIFICATION DRF PERSONNALISÉE
# ============================================================================

from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import exceptions

class CustomJWTAuthentication(BaseAuthentication):
    """
    Classe d'authentification personnalisée pour DRF
    qui gère les modèles Arbitre, Commissaire et Admin
    """
    
    def authenticate(self, request):
        """
        Authentifie l'utilisateur via JWT et retourne un tuple (user, auth)
        """
        try:
            # Récupérer le token depuis les headers
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if not auth_header.startswith('Bearer '):
                return None
            
            token = auth_header.split(' ')[1]
            
            # Utiliser l'authentification JWT standard
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user_id = validated_token['user_id']
            
            # Récupérer l'utilisateur depuis nos modèles
            user = None
            
            # Essayer Admin
            try:
                user = Admin.objects.get(id=user_id, is_active=True)
            except Admin.DoesNotExist:
                pass
            
            # Essayer Arbitre
            if not user:
                try:
                    user = Arbitre.objects.get(id=user_id, is_active=True)
                except Arbitre.DoesNotExist:
                    pass
            
            # Essayer Commissaire
            if not user:
                try:
                    user = Commissaire.objects.get(id=user_id, is_active=True)
                except Commissaire.DoesNotExist:
                    pass
            
            if user:
                print(f"🔐 DRF Auth - Utilisateur authentifié: {user.get_full_name()} ({user.__class__.__name__})")
                return (user, validated_token)
            else:
                print(f"❌ DRF Auth - Aucun utilisateur trouvé pour l'ID: {user_id}")
                return None
                
        except (InvalidToken, TokenError) as e:
            print(f"❌ DRF Auth - Token JWT invalide: {e}")
            return None
        except Exception as e:
            print(f"❌ DRF Auth - Erreur d'authentification: {e}")
            return None
    
    def authenticate_header(self, request):
        """
        Retourne l'en-tête d'authentification requis
        """
        return 'Bearer realm="api"'
