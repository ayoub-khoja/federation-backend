#!/usr/bin/env python3
"""
Diagnostic rapide du système de notifications push
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import Arbitre, PushSubscription
from matches.models import Designation, Match
from notifications.services import push_service

def diagnostic_rapide():
    """Diagnostic rapide du système de notifications"""
    
    print("🔍 DIAGNOSTIC RAPIDE DU SYSTÈME DE NOTIFICATIONS")
    print("=" * 60)
    
    # 1. Configuration VAPID
    print("\n🔑 CONFIGURATION VAPID:")
    try:
        from vapid_config import VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_EMAIL
        print(f"  ✅ Clés VAPID configurées")
        print(f"  📧 Email: {VAPID_EMAIL}")
        print(f"  🔑 Clé privée: {len(VAPID_PRIVATE_KEY)} caractères")
        print(f"  🔑 Clé publique: {len(VAPID_PUBLIC_KEY)} caractères")
    except ImportError:
        print("  ❌ Configuration VAPID manquante")
        return False
    
    # 2. État des abonnements
    print("\n📱 ÉTAT DES ABONNEMENTS:")
    total_subscriptions = PushSubscription.objects.count()
    active_subscriptions = PushSubscription.objects.filter(is_active=True).count()
    
    print(f"  Total: {total_subscriptions}")
    print(f"  Actifs: {active_subscriptions}")
    print(f"  Inactifs: {total_subscriptions - active_subscriptions}")
    
    if active_subscriptions == 0:
        print("  ⚠️  Aucun abonnement actif")
        return False
    
    # 3. Arbitres avec abonnements
    print("\n👥 ARBITRES ABONNÉS:")
    arbitres_abonnes = []
    for subscription in PushSubscription.objects.filter(is_active=True):
        arbitre = subscription.arbitre
        arbitres_abonnes.append(arbitre)
        print(f"  ✅ {arbitre.get_full_name()} - {arbitre.email}")
    
    # 4. Test rapide d'envoi
    print(f"\n🧪 TEST RAPIDE D'ENVOI:")
    if arbitres_abonnes:
        arbitre_test = arbitres_abonnes[0]
        print(f"  Test avec: {arbitre_test.get_full_name()}")
        
        try:
            result = push_service.send_notification_to_arbitres(
                arbitres=[arbitre_test],
                title="🔍 Test de Diagnostic",
                body="Test rapide du système de notifications",
                data={'type': 'diagnostic', 'timestamp': 'now'},
                tag='diagnostic'
            )
            
            if result.get('success', 0) > 0:
                print("  ✅ Test réussi!")
            else:
                print(f"  ❌ Test échoué: {result}")
                
        except Exception as e:
            print(f"  ❌ Erreur: {e}")
    
    # 5. Résumé
    print("\n📊 RÉSUMÉ:")
    print(f"  Configuration VAPID: {'✅' if 'VAPID_PRIVATE_KEY' in locals() else '❌'}")
    print(f"  Abonnements actifs: {active_subscriptions}")
    print(f"  Arbitres abonnés: {len(arbitres_abonnes)}")
    print(f"  Test d'envoi: {'✅' if arbitres_abonnes and 'result' in locals() and result.get('success', 0) > 0 else '❌'}")
    
    return True

if __name__ == "__main__":
    success = diagnostic_rapide()
    print(f"\n{'✅' if success else '❌'} DIAGNOSTIC TERMINÉ")

