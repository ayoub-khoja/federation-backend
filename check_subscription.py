#!/usr/bin/env python3
"""
Script pour vérifier l'état des abonnements push
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import Arbitre, PushSubscription
from django.utils import timezone

def check_subscriptions():
    """Vérifier l'état des abonnements push"""
    
    print("🔍 VÉRIFICATION DES ABONNEMENTS PUSH")
    print("=" * 50)
    
    # 1. Vérifier tous les arbitres
    print("\n👥 ARBITRES ET LEURS ABONNEMENTS")
    
    arbitres = Arbitre.objects.filter(is_active=True)
    total_arbitres = arbitres.count()
    
    print(f"📊 Total arbitres actifs: {total_arbitres}")
    
    for arbitre in arbitres:
        print(f"\n👤 {arbitre.get_full_name()} (ID: {arbitre.id})")
        
        # Vérifier les abonnements
        subscriptions = PushSubscription.objects.filter(arbitre=arbitre)
        total_subs = subscriptions.count()
        active_subs = subscriptions.filter(is_active=True).count()
        
        print(f"  📱 Abonnements totaux: {total_subs}")
        print(f"  ✅ Abonnements actifs: {active_subs}")
        
        if total_subs > 0:
            for sub in subscriptions:
                status = "✅ ACTIF" if sub.is_active else "❌ INACTIF"
                created = sub.created_at.strftime("%d/%m/%Y %H:%M")
                print(f"    - {status} | Créé: {created}")
                print(f"      Endpoint: {sub.endpoint[:50]}...")
        else:
            print("  ❌ Aucun abonnement")
    
    # 2. Statistiques globales
    print("\n📊 STATISTIQUES GLOBALES")
    
    total_subscriptions = PushSubscription.objects.count()
    active_subscriptions = PushSubscription.objects.filter(is_active=True).count()
    
    print(f"📱 Total abonnements: {total_subscriptions}")
    print(f"✅ Abonnements actifs: {active_subscriptions}")
    print(f"❌ Abonnements inactifs: {total_subscriptions - active_subscriptions}")
    
    # 3. Recommandations
    print("\n💡 RECOMMANDATIONS")
    
    if active_subscriptions == 0:
        print("🚨 Aucun abonnement actif !")
        print("   → Les arbitres doivent se réabonner aux notifications")
        print("   → Utilisez le script force_resubscribe.js dans le navigateur")
    elif active_subscriptions < total_arbitres:
        print("⚠️  Certains arbitres n'ont pas d'abonnement actif")
        print("   → Vérifiez les arbitres sans abonnement")
    else:
        print("✅ Tous les arbitres ont des abonnements actifs")
        print("   → Les notifications devraient fonctionner")
    
    return active_subscriptions > 0

if __name__ == "__main__":
    success = check_subscriptions()
    sys.exit(0 if success else 1)
