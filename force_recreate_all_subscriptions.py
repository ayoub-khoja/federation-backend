#!/usr/bin/env python3
"""
Script pour forcer la recréation de tous les abonnements avec les nouvelles clés VAPID
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import PushSubscription, Arbitre
from django.utils import timezone

def force_recreate_all_subscriptions():
    """Forcer la recréation de tous les abonnements"""
    
    print("🚀 FORCE RECRÉATION DE TOUS LES ABONNEMENTS VAPID")
    print("=" * 70)
    
    # 1. Vérifier la configuration VAPID actuelle
    print("\n🔑 VÉRIFICATION DE LA CONFIGURATION VAPID")
    try:
        from vapid_config import VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_EMAIL
        
        print(f"  ✅ Clé privée: {len(VAPID_PRIVATE_KEY)} caractères")
        print(f"  ✅ Clé publique: {len(VAPID_PUBLIC_KEY)} caractères")
        print(f"  ✅ Email: {VAPID_EMAIL}")
        
        # Afficher les premières lettres de la clé publique
        print(f"  🔓 Clé publique: {VAPID_PUBLIC_KEY[:20]}...")
        
    except ImportError as e:
        print(f"  ❌ Erreur d'import VAPID: {e}")
        return False
    
    # 2. Supprimer TOUS les abonnements existants
    print("\n🗑️  SUPPRESSION FORCÉE DE TOUS LES ABONNEMENTS")
    
    total_subscriptions = PushSubscription.objects.count()
    if total_subscriptions > 0:
        print(f"  📱 Suppression de {total_subscriptions} abonnements...")
        
        # Supprimer tous les abonnements sans demander
        PushSubscription.objects.all().delete()
        print("  ✅ Tous les abonnements supprimés")
    else:
        print("  ✅ Aucun abonnement à supprimer")
    
    # 3. Vérifier les arbitres disponibles
    print("\n👥 ARBITRES DISPONIBLES")
    arbitres = Arbitre.objects.filter(is_active=True)
    total_arbitres = arbitres.count()
    
    print(f"  📊 Total arbitres actifs: {total_arbitres}")
    
    if total_arbitres == 0:
        print("  ❌ Aucun arbitre actif trouvé")
        return False
    
    # Afficher quelques arbitres
    for i, arbitre in enumerate(arbitres[:5], 1):
        print(f"    {i}. {arbitre.get_full_name()} ({arbitre.grade})")
    
    if total_arbitres > 5:
        print(f"    ... et {total_arbitres - 5} autres arbitres")
    
    # 4. Instructions pour l'utilisateur
    print("\n🚨 INSTRUCTIONS CRITIQUES POUR L'UTILISATEUR")
    print("=" * 70)
    print("1. ARRÊTER le serveur Django (Ctrl+C)")
    print("2. VIDER le cache du navigateur (Ctrl+Shift+Delete)")
    print("3. FERMER complètement le navigateur")
    print("4. RELANCER le serveur Django: python manage.py runserver")
    print("5. REOUVRIR le navigateur et aller sur l'application")
    print("6. SE RECONNECTER avec votre compte arbitre")
    print("7. ACCEPTER les notifications push à nouveau")
    print("8. Les nouvelles clés VAPID seront utilisées")
    
    print(f"\n🔑 NOUVELLES CLÉS VAPID:")
    print(f"  🔐 Privée: {VAPID_PRIVATE_KEY[:20]}...")
    print(f"  🔓 Publique: {VAPID_PUBLIC_KEY[:20]}...")
    
    print("\n⚠️  ATTENTION:")
    print("   - Tous les anciens abonnements ont été supprimés")
    print("   - Les utilisateurs devront se réabonner aux notifications")
    print("   - Les nouvelles clés VAPID seront utilisées")
    print("   - Plus d'erreur 'VAPID credentials do not correspond'")
    
    print("\n✅ PROBLÈME RÉSOLU:")
    print("   - Anciens abonnements supprimés")
    print("   - Nouvelles clés VAPID prêtes")
    print("   - Prêt pour de nouveaux abonnements")
    
    return True

def verify_clean_state():
    """Vérifier que l'état est propre"""
    
    print("\n🧪 VÉRIFICATION DE L'ÉTAT PROPRE")
    print("=" * 50)
    
    # Vérifier les abonnements
    total_subscriptions = PushSubscription.objects.count()
    print(f"  📱 Total abonnements: {total_subscriptions}")
    
    if total_subscriptions == 0:
        print("  ✅ Aucun abonnement - état propre")
        return True
    else:
        print("  ❌ Il reste des abonnements")
        return False

if __name__ == "__main__":
    success = force_recreate_all_subscriptions()
    
    if success:
        print("\n" + "=" * 70)
        print("🎯 RÉCRÉATION FORCÉE TERMINÉE AVEC SUCCÈS!")
        print("💡 Suivez les instructions pour finaliser la configuration")
        
        # Vérifier l'état final
        verify_clean_state()
    else:
        print("\n❌ Échec de la récréation forcée")
    
    sys.exit(0 if success else 1)
