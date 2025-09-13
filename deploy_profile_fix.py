#!/usr/bin/env python3
"""
Script de déploiement pour corriger l'erreur 403 sur l'endpoint profil arbitre
"""

import os
import sys
import django
from django.conf import settings

def setup_django():
    """Configuration Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings_production')
    django.setup()

def test_profile_endpoint_production():
    """Tester l'endpoint de profil en production"""
    print("🔍 Test de l'endpoint de profil en production")
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
        
        # Tester la vue
        response = arbitre_profile(request)
        
        print(f"📊 Status de la réponse: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ L'endpoint de profil fonctionne correctement")
            return True
        else:
            print(f"❌ L'endpoint retourne une erreur: {response.status_code}")
            print(f"📊 Détails: {response.data}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_arbitres_data():
    """Vérifier les données des arbitres"""
    print("\n🔍 Vérification des données des arbitres")
    print("=" * 60)
    
    try:
        from accounts.models import Arbitre
        
        arbitres_count = Arbitre.objects.count()
        active_arbitres = Arbitre.objects.filter(is_active=True).count()
        
        print(f"📊 Total des arbitres: {arbitres_count}")
        print(f"📊 Arbitres actifs: {active_arbitres}")
        
        if arbitres_count == 0:
            print("❌ Aucun arbitre trouvé en base de données")
            return False
        
        # Afficher quelques arbitres
        for arbitre in Arbitre.objects.all()[:3]:
            print(f"   - {arbitre.get_full_name()} (ID: {arbitre.id}, Actif: {arbitre.is_active})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def run_migrations():
    """Exécuter les migrations si nécessaire"""
    print("\n🔄 Vérification des migrations")
    print("=" * 60)
    
    try:
        from django.core.management import execute_from_command_line
        
        # Vérifier les migrations en attente
        execute_from_command_line(['manage.py', 'showmigrations', 'accounts'])
        
        # Appliquer les migrations si nécessaire
        execute_from_command_line(['manage.py', 'migrate', 'accounts', '--noinput'])
        
        print("✅ Migrations vérifiées et appliquées")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des migrations: {e}")
        return False

def test_authentication_flow():
    """Tester le flux d'authentification complet"""
    print("\n🔍 Test du flux d'authentification complet")
    print("=" * 60)
    
    try:
        from accounts.models import Arbitre
        from rest_framework_simplejwt.tokens import RefreshToken
        from django.test import RequestFactory
        from accounts.views import arbitre_login, arbitre_profile
        
        # Récupérer un arbitre
        arbitre = Arbitre.objects.first()
        if not arbitre:
            print("❌ Aucun arbitre trouvé")
            return False
        
        print(f"👤 Arbitre de test: {arbitre.get_full_name()}")
        
        # Test de connexion
        factory = RequestFactory()
        login_request = factory.post('/api/accounts/arbitres/login/', {
            'phone_number': arbitre.phone_number,
            'password': 'test123'  # Mot de passe de test
        }, content_type='application/json')
        
        # Note: Ceci nécessiterait un mot de passe valide
        print("⚠️ Test de connexion nécessite un mot de passe valide")
        
        # Test direct avec token
        refresh = RefreshToken.for_user(arbitre)
        access_token = str(refresh.access_token)
        
        profile_request = factory.get('/api/accounts/arbitres/profile/')
        profile_request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
        
        # Appliquer le middleware
        from accounts.middleware import CustomJWTAuthenticationMiddleware
        middleware = CustomJWTAuthenticationMiddleware(lambda req: None)
        middleware(profile_request)
        
        # Tester la vue de profil
        response = arbitre_profile(profile_request)
        
        print(f"📊 Status de la réponse: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Le flux d'authentification fonctionne correctement")
            return True
        else:
            print(f"❌ Erreur dans le flux d'authentification: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test du flux d'authentification: {e}")
        return False

def main():
    """Fonction principale"""
    print("🏁 Déploiement de la correction de l'endpoint profil arbitre")
    print("=" * 80)
    
    # Configuration Django
    setup_django()
    
    # Étapes de déploiement
    steps = [
        ("Vérification des données", verify_arbitres_data),
        ("Migrations", run_migrations),
        ("Test de l'endpoint", test_profile_endpoint_production),
        ("Test du flux d'authentification", test_authentication_flow),
    ]
    
    success = True
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ Échec de l'étape: {step_name}")
            success = False
        else:
            print(f"✅ {step_name} terminé avec succès")
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 Déploiement terminé avec succès!")
        print("🌐 L'endpoint de profil arbitre devrait maintenant fonctionner correctement")
        print("🔗 URL: https://federation-backend.onrender.com/api/accounts/arbitres/profile/")
        print("\n💡 Pour tester:")
        print("1. Connectez-vous avec un compte arbitre")
        print("2. Naviguez vers le profil")
        print("3. Vérifiez que les données s'affichent correctement")
    else:
        print("❌ Le déploiement a échoué")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


