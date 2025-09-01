"""
Middleware pour gérer l'authentification JWT avec les modèles personnalisés
"""
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.middleware import get_user
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import Admin, Arbitre, Commissaire

class CustomJWTAuthenticationMiddleware:
    """
    Middleware personnalisé pour gérer l'authentification JWT
    avec les modèles Admin, Arbitre et Commissaire
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()
    
    def __call__(self, request):
        # Vérifier si c'est une requête API
        if request.path.startswith('/api/'):
            # Essayer d'authentifier avec JWT
            try:
                # Récupérer le token depuis les headers
                auth_header = request.META.get('HTTP_AUTHORIZATION', '')
                if auth_header.startswith('Bearer '):
                    token = auth_header.split(' ')[1]
                    
                    # Valider le token JWT
                    validated_token = self.jwt_auth.get_validated_token(token)
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
                        request.user = user
                        request._cached_user = user
                        print(f"🔐 Utilisateur authentifié: {user.get_full_name()} ({user.__class__.__name__})")
                        
            except (InvalidToken, TokenError) as e:
                print(f"❌ Token JWT invalide: {e}")
                pass
            except Exception as e:
                print(f"❌ Erreur d'authentification JWT: {e}")
                pass
        
        response = self.get_response(request)
        return response

def get_user_jwt(request):
    """
    Fonction pour récupérer l'utilisateur authentifié via JWT
    """
    if not hasattr(request, '_cached_user'):
        request._cached_user = get_user(request)
    return request._cached_user
