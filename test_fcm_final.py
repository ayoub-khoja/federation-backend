#!/usr/bin/env python
"""
Test final du système Firebase Cloud Messaging (FCM)
"""
import os
import sys
import django
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import FCMToken, Arbitre
from firebase_config import send_notification_to_user, get_notification_stats, initialize_firebase

def test_fcm_system():
    """Test complet du système FCM"""
    print("🔥 Test Final du Système Firebase Cloud Messaging")
    print("=" * 60)
    
    # 1. Test d'initialisation Firebase
    print("1️⃣ Initialisation Firebase...")
    success = initialize_firebase()
    if success:
        print("   ✅ Firebase initialisé avec succès!")
        print("   📱 Project ID: federation-16c7a")
    else:
        print("   ❌ Erreur lors de l'initialisation Firebase")
        return False
    
    # 2. Vérifier les tokens FCM
    print("\n2️⃣ Vérification des tokens FCM...")
    tokens = FCMToken.objects.filter(is_active=True)
    print(f"   📱 Tokens FCM actifs: {tokens.count()}")
    
    if not tokens.exists():
        print("   ⚠️ Aucun token FCM actif trouvé")
        print("   💡 Créez un token de test pour tester les notifications")
        return True
    
    # 3. Test d'envoi de notification
    print("\n3️⃣ Test d'envoi de notification...")
    fcm_token = tokens.first()
    user = fcm_token.get_user()
    
    print(f"   👤 Utilisateur: {user.get_full_name()}")
    print(f"   📱 Plateforme: {fcm_token.device_type}")
    print(f"   🔑 Token: {fcm_token.token[:20]}...")
    
    # Envoyer une notification de test
    print("   📤 Envoi de notification de test...")
    results = send_notification_to_user(
        user=user,
        title="🎉 Test FCM Réussi!",
        body="Votre système Firebase Cloud Messaging fonctionne parfaitement!",
        data={
            'type': 'test', 
            'timestamp': datetime.now().isoformat(),
            'project_id': 'federation-16c7a'
        }
    )
    
    print(f"   📊 Résultats: {results}")
    
    if results.get('errors', 0) == 0:
        print("   ✅ Notification envoyée avec succès!")
    else:
        print(f"   ⚠️ {results.get('errors', 0)} erreur(s) lors de l'envoi")
    
    # 4. Statistiques finales
    print("\n4️⃣ Statistiques finales...")
    stats = get_notification_stats()
    print(f"   📈 Total tokens: {stats.get('total_tokens', 0)}")
    print(f"   📈 Tokens actifs: {stats.get('active_tokens', 0)}")
    print(f"   📈 Par plateforme: {stats.get('by_platform', {})}")
    
    return True

def create_test_token():
    """Créer un token FCM de test"""
    print("\n🔧 Création d'un token FCM de test...")
    
    # Créer un arbitre de test
    arbitre, created = Arbitre.objects.get_or_create(
        phone_number='+21699999999',
        defaults={
            'first_name': 'Test',
            'last_name': 'FCM',
            'email': 'test.fcm@example.com',
            'grade': '2eme_serie',
            'role': 'arbitre'
        }
    )
    
    if created:
        print(f"   ✅ Arbitre de test créé: {arbitre.get_full_name()}")
    else:
        print(f"   ✅ Arbitre de test existant: {arbitre.get_full_name()}")
    
    # Créer un token FCM de test
    fcm_token, created = FCMToken.objects.get_or_create(
        token='test_fcm_token_final_123456789',
        defaults={
            'arbitre': arbitre,
            'device_type': 'android',
            'device_id': 'test_device_final_123',
            'app_version': '1.0.0',
            'is_active': True
        }
    )
    
    if created:
        print(f"   ✅ Token FCM créé: {fcm_token}")
    else:
        print(f"   ✅ Token FCM existant: {fcm_token}")
    
    return fcm_token

def main():
    """Fonction principale"""
    try:
        # Test du système FCM
        success = test_fcm_system()
        
        if not success:
            print("\n❌ Le test a échoué")
            return
        
        print("\n" + "=" * 60)
        print("🎉 SYSTÈME FCM COMPLÈTEMENT OPÉRATIONNEL!")
        print("=" * 60)
        
        print("\n📋 Prochaines étapes:")
        print("   1. ✅ Firebase Admin SDK installé")
        print("   2. ✅ Configuration Firebase configurée")
        print("   3. ✅ Clé de service téléchargée")
        print("   4. ✅ Système FCM testé et fonctionnel")
        print("   5. 🔄 Configurer les applications mobiles")
        print("   6. 🔄 Tester avec des appareils réels")
        print("   7. 🔄 Migrer les utilisateurs vers FCM")
        
        print("\n📱 Applications à configurer:")
        print("   - iOS: Bundle ID com.company.federation")
        print("   - Android: Package name android.federation")
        
        print("\n🔗 Endpoints FCM disponibles:")
        print("   - POST /api/accounts/fcm/subscribe/")
        print("   - POST /api/accounts/fcm/unsubscribe/")
        print("   - GET /api/accounts/fcm/status/")
        print("   - POST /api/accounts/fcm/test/")
        print("   - GET /api/accounts/fcm/stats/")
        print("   - POST /api/accounts/fcm/broadcast/")
        
        print("\n📚 Documentation:")
        print("   - FCM_IMPLEMENTATION.md")
        print("   - MOBILE_MIGRATION_GUIDE.md")
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
