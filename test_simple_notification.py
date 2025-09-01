#!/usr/bin/env python3
"""
Test simple d'envoi de notification
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import Arbitre, PushSubscription
from notifications.services import push_service

def test_simple_notification():
    """Test simple d'envoi de notification"""
    
    print("🧪 TEST SIMPLE DE NOTIFICATION")
    print("=" * 50)
    
    # 1. Vérifier les abonnements actifs
    print("\n📱 ABONNEMENTS ACTIFS:")
    active_subscriptions = PushSubscription.objects.filter(is_active=True)
    
    if not active_subscriptions.exists():
        print("  ❌ Aucun abonnement actif trouvé")
        print("  💡 Les arbitres doivent d'abord s'abonner aux notifications")
        return False
    
    print(f"  ✅ {active_subscriptions.count()} abonnement(s) actif(s)")
    
    # 2. Prendre le premier abonnement pour le test
    subscription = active_subscriptions.first()
    arbitre = subscription.arbitre
    
    print(f"\n👤 TEST AVEC: {arbitre.get_full_name()}")
    print(f"   Email: {arbitre.email}")
    print(f"   Endpoint: {subscription.endpoint[:50]}...")
    
    # 3. Envoyer une notification de test
    print("\n🔔 ENVOI DE NOTIFICATION DE TEST:")
    
    try:
        result = push_service.send_notification_to_arbitres(
            arbitres=[arbitre],
            title="🧪 Test Simple",
            body="Ceci est un test simple du système de notifications",
            data={'type': 'simple_test', 'message': 'Hello World!'},
            tag='simple_test'
        )
        
        print(f"  Résultat: {result}")
        
        if result.get('success', 0) > 0:
            print("  ✅ Notification envoyée avec succès!")
            print("  🎯 Vérifiez votre navigateur pour la notification")
        else:
            print("  ❌ Échec de l'envoi")
            if result.get('errors'):
                print(f"  Erreurs: {result['errors']}")
                
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        import traceback
        print(f"  Stack trace: {traceback.format_exc()}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_simple_notification()
    
    if success:
        print("\n🎉 TEST RÉUSSI!")
        print("  Le système de notifications fonctionne correctement")
    else:
        print("\n❌ TEST ÉCHOUÉ")
        print("  Vérifiez la configuration et les abonnements")
    
    print("\n" + "=" * 50)
    print("✅ TEST TERMINÉ")

