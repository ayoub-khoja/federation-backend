#!/usr/bin/env python3
"""
Script de diagnostic pour l'erreur 403 sur l'endpoint profil arbitre
"""

import os
import sys
import django
from django.conf import settings

def setup_django():
    """Configuration Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
    django.setup()

def test_arbitre_authentication():
    """Tester l'authentification des arbitres"""
    print("🔍 Test de l'authentification des arbitres")
    print("=" * 60)
    
    try:
        from accounts.models import Arbitre, Admin, Commissaire
        from django.contrib.contenttypes.models import ContentType
        from rest_framework_simplejwt.tokens import RefreshToken
        
        # Vérifier les arbitres existants
        arbitres_count = Arbitre.objects.count()
        print(f"📊 Nombre d'arbitres en base: {arbitres_count}")
        
        if arbitres_count == 0:
            print("❌ Aucun arbitre trouvé en base de données")
            return False
        
        # Tester avec le premier arbitre
        arbitre = Arbitre.objects.first()
        print(f"👤 Arbitre de test: {arbitre.get_full_name()}")
        print(f"   ID: {arbitre.id}")
        print(f"   Type: {type(arbitre)}")
        print(f"   is_active: {arbitre.is_active}")
        
        # Générer un token JWT pour cet arbitre
        refresh = RefreshToken.for_user(arbitre)
        access_token = str(refresh.access_token)
        
        print(f"🔑 Token généré: {access_token[:50]}...")
        
        # Tester l'authentification avec le middleware
        from accounts.middleware import CustomJWTAuthenticationMiddleware
        from django.test import RequestFactory
        
        # Créer une requête de test
        factory = RequestFactory()
        request = factory.get('/api/accounts/arbitres/profile/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
        
        # Appliquer le middleware
        middleware = CustomJWTAuthenticationMiddleware(lambda req: None)
        middleware(request)
        
        print(f"🔍 Utilisateur après middleware: {request.user}")
        print(f"🔍 Type: {type(request.user)}")
        print(f"🔍 is_authenticated: {request.user.is_authenticated}")
        print(f"🔍 isinstance(Arbitre): {isinstance(request.user, Arbitre)}")
        
        if isinstance(request.user, Arbitre):
            print("✅ L'authentification fonctionne correctement")
            return True
        else:
            print("❌ L'utilisateur n'est pas reconnu comme un Arbitre")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_profile_endpoint():
    """Tester l'endpoint de profil"""
    print("\n🔍 Test de l'endpoint de profil")
    print("=" * 60)
    
    try:
        from accounts.models import Arbitre
        from rest_framework_simplejwt.tokens import RefreshToken
        from django.test import RequestFactory
        from accounts.views import arbitre_profile
        from rest_framework.response import Response
        
        # Récupérer un arbitre
        arbitre = Arbitre.objects.first()
        if not arbitre:
            print("❌ Aucun arbitre trouvé")
            return False
        
        # Générer un token
        refresh = RefreshToken.for_user(arbitre)
        access_token = str(refresh.access_token)
        
        # Créer une requête
        factory = RequestFactory()
        request = factory.get('/api/accounts/arbitres/profile/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
        
        # Appliquer le middleware
        from accounts.middleware import CustomJWTAuthenticationMiddleware
        middleware = CustomJWTAuthenticationMiddleware(lambda req: None)
        middleware(request)
        
        # Tester la vue
        response = arbitre_profile(request)
        
        print(f"📊 Status de la réponse: {response.status_code}")
        print(f"📊 Contenu de la réponse: {response.data}")
        
        if response.status_code == 200:
            print("✅ L'endpoint de profil fonctionne correctement")
            return True
        else:
            print(f"❌ L'endpoint retourne une erreur: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test de l'endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_profile_endpoint():
    """Corriger l'endpoint de profil"""
    print("\n🔧 Correction de l'endpoint de profil")
    print("=" * 60)
    
    try:
        # Lire le fichier views.py
        views_file = 'accounts/views.py'
        
        with open(views_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer la logique de vérification
        old_code = '''    if not isinstance(request.user, Arbitre):
        print(f"❌ DEBUG - L'utilisateur n'est pas un Arbitre, c'est un: {type(request.user)}")
        return Response({'detail': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)'''
        
        new_code = '''    # Vérification améliorée de l'utilisateur
    if not request.user.is_authenticated:
        print(f"❌ DEBUG - Utilisateur non authentifié")
        return Response({'detail': 'Authentification requise'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Vérifier si c'est un arbitre ou un utilisateur avec les bonnes permissions
    if not isinstance(request.user, Arbitre):
        print(f"❌ DEBUG - L'utilisateur n'est pas un Arbitre, c'est un: {type(request.user)}")
        # Essayer de récupérer l'arbitre par ID si c'est un utilisateur générique
        try:
            from accounts.models import Arbitre
            arbitre = Arbitre.objects.get(id=request.user.id, is_active=True)
            request.user = arbitre  # Remplacer l'utilisateur par l'arbitre
            print(f"✅ DEBUG - Arbitre récupéré: {arbitre.get_full_name()}")
        except Arbitre.DoesNotExist:
            return Response({
                'detail': 'Accès non autorisé - Seuls les arbitres peuvent accéder à ce profil',
                'user_type': str(type(request.user).__name__)
            }, status=status.HTTP_403_FORBIDDEN)'''
        
        if old_code in content:
            content = content.replace(old_code, new_code)
            
            # Écrire le fichier modifié
            with open(views_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Endpoint de profil corrigé")
            return True
        else:
            print("⚠️ Code à remplacer non trouvé, vérification manuelle nécessaire")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")
        return False

def main():
    """Fonction principale"""
    print("🏁 Diagnostic de l'erreur 403 sur l'endpoint profil arbitre")
    print("=" * 80)
    
    # Configuration Django
    setup_django()
    
    # Tests
    auth_ok = test_arbitre_authentication()
    endpoint_ok = test_profile_endpoint()
    
    if not auth_ok or not endpoint_ok:
        print("\n🔧 Tentative de correction...")
        fix_ok = fix_profile_endpoint()
        
        if fix_ok:
            print("\n🔄 Test après correction...")
            endpoint_ok = test_profile_endpoint()
    
    print("\n" + "=" * 80)
    if auth_ok and endpoint_ok:
        print("✅ Le problème est résolu!")
        print("🌐 L'endpoint de profil devrait maintenant fonctionner correctement")
    else:
        print("❌ Le problème persiste")
        print("🔧 Vérifiez les logs ci-dessus pour plus de détails")

if __name__ == "__main__":
    main()



