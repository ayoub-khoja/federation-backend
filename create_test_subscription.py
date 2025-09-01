#!/usr/bin/env python3
"""
Script pour créer un abonnement de test pour un arbitre
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import Arbitre, PushSubscription
from django.utils import timezone

def create_test_subscription():
    """Créer un abonnement de test pour l'arbitre ID 14"""
    
    print("🔧 CRÉATION D'UN ABONNEMENT DE TEST")
    print("=" * 50)
    
    # 1. Récupérer l'arbitre
    try:
        arbitre = Arbitre.objects.get(id=14)
        print(f"👤 Arbitre: {arbitre.get_full_name()} (ID: {arbitre.id})")
    except Arbitre.DoesNotExist:
        print("❌ Arbitre ID 14 non trouvé")
        return False
    
    # 2. Vérifier s'il a déjà des abonnements
    existing_subs = PushSubscription.objects.filter(arbitre=arbitre)
    print(f"📱 Abonnements existants: {existing_subs.count()}")
    
    if existing_subs.exists():
        print("  → Suppression des anciens abonnements...")
        existing_subs.delete()
        print("  ✅ Anciens abonnements supprimés")
    
    # 3. Créer un abonnement de test (simulation)
    try:
        # Endpoint FCM de test (similaire à celui qui fonctionne)
        test_endpoint = "https://fcm.googleapis.com/fcm/send/TEST_SUBSCRIPTION_KEY_12345"
        
        subscription = PushSubscription.objects.create(
            arbitre=arbitre,
            endpoint=test_endpoint,
            p256dh="TEST_P256DH_KEY_12345",
            auth="TEST_AUTH_KEY_12345",
            is_active=True,
            created_at=timezone.now()
        )
        
        print(f"✅ Abonnement de test créé avec l'ID: {subscription.id}")
        print(f"   Endpoint: {subscription.endpoint[:50]}...")
        print(f"   Actif: {subscription.is_active}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        return False
    
    # 4. Vérifier l'état final
    print("\n🔍 VÉRIFICATION FINALE")
    
    final_subs = PushSubscription.objects.filter(arbitre=arbitre, is_active=True)
    print(f"📱 Abonnements actifs: {final_subs.count()}")
    
    if final_subs.exists():
        print("✅ L'arbitre a maintenant un abonnement actif")
        print("💡 Vous pouvez maintenant tester les notifications")
    else:
        print("❌ Aucun abonnement actif trouvé")
    
    return True

if __name__ == "__main__":
    success = create_test_subscription()
    sys.exit(0 if success else 1)
