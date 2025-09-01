#!/usr/bin/env python3
"""
Script pour forcer la recréation des abonnements push
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import PushSubscription

def force_recreate_subscriptions():
    """Forcer la recréation de tous les abonnements push"""
    
    print("🔄 FORCER LA RECRÉATION DES ABONNEMENTS PUSH")
    print("=" * 60)
    
    # 1. Afficher l'état actuel
    print("\n📱 ÉTAT ACTUEL:")
    total_subscriptions = PushSubscription.objects.count()
    active_subscriptions = PushSubscription.objects.filter(is_active=True).count()
    
    print(f"  Total abonnements: {total_subscriptions}")
    print(f"  Abonnements actifs: {active_subscriptions}")
    
    if total_subscriptions == 0:
        print("  ✅ Aucun abonnement à recréer")
        return True
    
    # 2. Demander confirmation
    print(f"\n⚠️  ATTENTION: Ce script va supprimer {total_subscriptions} abonnements existants.")
    print("   Cela forcera les utilisateurs à se réabonner aux notifications.")
    
    response = input("\n❓ Continuer ? (oui/non): ").lower().strip()
    if response not in ['oui', 'o', 'yes', 'y']:
        print("  ❌ Opération annulée")
        return False
    
    # 3. Supprimer tous les abonnements
    print("\n🗑️  SUPPRESSION DES ABONNEMENTS...")
    deleted_count = 0
    
    for subscription in PushSubscription.objects.all():
        arbitre_name = subscription.arbitre.get_full_name()
        endpoint = subscription.endpoint[:30] + "..." if len(subscription.endpoint) > 30 else subscription.endpoint
        print(f"  Suppression: {arbitre_name} - {endpoint}")
        subscription.delete()
        deleted_count += 1
    
    print(f"\n✅ {deleted_count} abonnements supprimés avec succès")
    
    # 4. Instructions pour les utilisateurs
    print("\n💡 INSTRUCTIONS POUR LES UTILISATEURS:")
    print("  1. Les utilisateurs devront se reconnecter")
    print("  2. Accepter les notifications push à nouveau")
    print("  3. Le navigateur créera de nouveaux abonnements")
    print("  4. Les notifications fonctionneront avec les nouvelles clés VAPID")
    
    # 5. Vérification finale
    final_count = PushSubscription.objects.count()
    print(f"\n🔍 VÉRIFICATION FINALE:")
    print(f"  Abonnements restants: {final_count}")
    
    if final_count == 0:
        print("  ✅ Tous les abonnements ont été supprimés")
        print("  🎯 Les utilisateurs devront se réabonner")
        return True
    else:
        print("  ❌ Il reste des abonnements")
        return False

if __name__ == "__main__":
    success = force_recreate_subscriptions()
    sys.exit(0 if success else 1)

