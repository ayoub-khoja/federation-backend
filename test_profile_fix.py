#!/usr/bin/env python3
"""
Script de test pour vérifier la correction de l'endpoint profil arbitre
"""

import os
import sys
import django
from django.conf import settings
import requests
import json

def setup_django():
    """Configuration Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
    django.setup()

def test_local_profile():
    """Tester l'endpoint de profil en local"""
    print("🔍 Test de l'endpoint de profil en local")
    print("=" * 60)
    
    try:
        from accounts.models import Arbitre
        from rest_framework_simplejwt.tokens import RefreshToken
        from django.test import RequestFactory
        from accounts.views import arbitre_profile
        
        # Récupérer un arbitre
        arbitre = Arbitre.objects.first()
        if not arbitre:
            print("❌ Aucun arbitre trouvé en base de données")
            return False
        
        print(f"👤 Arbitre de test: {arbitre.get_full_name()}")
        print(f"   ID: {arbitre.id}")
        print(f"   Email: {arbitre.email}")
        
        # Générer un token JWT
        refresh = RefreshToken.for_user(arbitre)
        access_token = str(refresh.access_token)
        
        print(f"🔑 Token généré: {access_token[:50]}...")
        
        # Créer une requête
        factory = RequestFactory()
        request = factory.get('/api/accounts/arbitres/profile/')
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
        
        # Appliquer le middleware d'authentification
        from accounts.middleware import CustomJWTAuthenticationMiddleware
        middleware = CustomJWTAuthenticationMiddleware(lambda req: None)
        middleware(request)
        
        print(f"🔍 Utilisateur après middleware: {request.user}")
        print(f"🔍 Type: {type(request.user)}")
        print(f"🔍 is_authenticated: {request.user.is_authenticated}")
        
        # Tester la vue
        response = arbitre_profile(request)
        
        print(f"📊 Status de la réponse: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ L'endpoint de profil fonctionne correctement")
            print(f"📊 Données retournées: {json.dumps(response.data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ L'endpoint retourne une erreur: {response.status_code}")
            print(f"📊 Détails de l'erreur: {response.data}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_production_profile():
    """Tester l'endpoint de profil en production"""
    print("\n🔍 Test de l'endpoint de profil en production")
    print("=" * 60)
    
    production_url = "https://federation-backend.onrender.com/api/accounts/arbitres/profile/"
    
    try:
        # Note: Pour tester en production, vous devez avoir un token valide
        # Ceci est un exemple de test avec un token factice
        test_token = "test_token_here"
        
        headers = {
            'Authorization': f'Bearer {test_token}',
            'Content-Type': 'application/json'
        }
        
        print(f"🌐 Test de l'URL: {production_url}")
        print(f"🔑 Token utilisé: {test_token[:20]}...")
        
        response = requests.get(production_url, headers=headers, timeout=10)
        
        print(f"📊 Status de la réponse: {response.status_code}")
        print(f"📊 Headers de la réponse: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ L'endpoint de profil fonctionne en production")
            return True
        elif response.status_code == 401:
            print("⚠️ Erreur d'authentification - Token invalide ou expiré")
            return False
        elif response.status_code == 403:
            print("❌ Erreur d'autorisation - L'utilisateur n'a pas les permissions")
            print(f"📊 Détails: {response.text}")
            return False
        else:
            print(f"❌ Erreur inattendue: {response.status_code}")
            print(f"📊 Détails: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion au serveur de production")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test de production: {e}")
        return False

def create_test_arbitre():
    """Créer un arbitre de test si nécessaire"""
    print("\n🔧 Création d'un arbitre de test")
    print("=" * 60)
    
    try:
        from accounts.models import Arbitre, Ligue
        
        # Vérifier s'il y a déjà des arbitres
        if Arbitre.objects.exists():
            print("✅ Des arbitres existent déjà en base")
            return True
        
        # Créer une ligue de test si nécessaire
        ligue, created = Ligue.objects.get_or_create(
            nom="Ligue Test",
            defaults={'description': 'Ligue de test pour les arbitres'}
        )
        
        if created:
            print(f"✅ Ligue de test créée: {ligue.nom}")
        
        # Créer un arbitre de test
        arbitre = Arbitre.objects.create(
            phone_number="+216123456789",
            first_name="Test",
            last_name="Arbitre",
            email="test.arbitre@example.com",
            grade="Fédéral 1",
            ligue=ligue,
            is_active=True
        )
        
        print(f"✅ Arbitre de test créé: {arbitre.get_full_name()}")
        print(f"   ID: {arbitre.id}")
        print(f"   Email: {arbitre.email}")
        print(f"   Téléphone: {arbitre.phone_number}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'arbitre de test: {e}")
        return False

def main():
    """Fonction principale"""
    print("🏁 Test de la correction de l'endpoint profil arbitre")
    print("=" * 80)
    
    # Configuration Django
    setup_django()
    
    # Créer un arbitre de test si nécessaire
    create_test_arbitre()
    
    # Tests
    local_ok = test_local_profile()
    production_ok = test_production_profile()
    
    print("\n" + "=" * 80)
    print("📊 Résumé des tests")
    print("=" * 80)
    print(f"🏠 Test local: {'✅ Réussi' if local_ok else '❌ Échec'}")
    print(f"🌐 Test production: {'✅ Réussi' if production_ok else '❌ Échec'}")
    
    if local_ok:
        print("\n🎉 La correction fonctionne en local!")
        print("🚀 Vous pouvez maintenant déployer en production")
    else:
        print("\n❌ La correction ne fonctionne pas en local")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    if not production_ok:
        print("\n💡 Pour tester en production:")
        print("1. Déployer les changements sur Render")
        print("2. Obtenir un token JWT valide d'un arbitre")
        print("3. Tester avec ce token")

if __name__ == "__main__":
    main()



