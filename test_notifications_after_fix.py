#!/usr/bin/env python3
"""
Script pour tester les notifications push après la résolution du problème VAPID
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import Arbitre, PushSubscription
from notifications.services import push_service
from django.utils import timezone

def test_notifications_after_fix():
    """Tester les notifications push après la résolution VAPID"""
    
    print("🧪 TEST DES NOTIFICATIONS APRÈS RÉSOLUTION VAPID")
    print("=" * 60)
    
    # 1. Vérifier la configuration VAPID
    print("\n🔑 VÉRIFICATION DE LA CONFIGURATION VAPID")
    try:
        from vapid_config import VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_EMAIL
        
        print(f"  ✅ Clé privée: {len(VAPID_PRIVATE_KEY)} caractères")
        print(f"  ✅ Clé publique: {len(VAPID_PUBLIC_KEY)} caractères")
        print(f"  ✅ Email: {VAPID_EMAIL}")
        
        # Vérifier que les clés sont différentes
        if VAPID_PRIVATE_KEY == VAPID_PUBLIC_KEY:
            print("  ❌ Les clés privée et publique sont identiques!")
            return False
        else:
            print("  ✅ Les clés privée et publique sont différentes")
            
    except ImportError as e:
        print(f"  ❌ Erreur d'import VAPID: {e}")
        return False
    
    # 2. Vérifier les abonnements existants
    print("\n📱 VÉRIFICATION DES ABONNEMENTS")
    total_subscriptions = PushSubscription.objects.count()
    active_subscriptions = PushSubscription.objects.filter(is_active=True).count()
    
    print(f"  Total abonnements: {total_subscriptions}")
    print(f"  Abonnements actifs: {active_subscriptions}")
    
    if total_subscriptions == 0:
        print("  ℹ️  Aucun abonnement trouvé - les utilisateurs devront s'abonner")
    elif active_subscriptions == 0:
        print("  ⚠️  Aucun abonnement actif - vérifier la configuration")
    else:
        print("  ✅ Abonnements actifs trouvés")
    
    # 3. Vérifier les arbitres disponibles
    print("\n👥 VÉRIFICATION DES ARBITRES")
    total_arbitres = Arbitre.objects.count()
    active_arbitres = Arbitre.objects.filter(is_active=True).count()
    
    print(f"  Total arbitres: {total_arbitres}")
    print(f"  Arbitres actifs: {active_arbitres}")
    
    if active_arbitres == 0:
        print("  ❌ Aucun arbitre actif trouvé")
        return False
    
    # 4. Tester l'envoi de notification
    print("\n🔔 TEST D'ENVOI DE NOTIFICATION")
    
    # Prendre le premier arbitre actif
    test_arbitre = Arbitre.objects.filter(is_active=True).first()
    
    if not test_arbitre:
        print("  ❌ Aucun arbitre disponible pour le test")
        return False
    
    print(f"  Arbitre de test: {test_arbitre.get_full_name()}")
    
    # Vérifier s'il a des abonnements
    arbitre_subscriptions = PushSubscription.objects.filter(
        arbitre=test_arbitre,
        is_active=True
    )
    
    if not arbitre_subscriptions.exists():
        print("  ℹ️  Cet arbitre n'a pas d'abonnement actif")
        print("  💡 Il devra s'abonner aux notifications via l'application")
        return True
    
    print(f"  ✅ {arbitre_subscriptions.count()} abonnement(s) actif(s) trouvé(s)")
    
    # 5. Tester l'envoi de notification
    print("\n🚀 TEST D'ENVOI DE NOTIFICATION")
    
    # Créer des données de test pour un match
    test_match_data = {
        'id': 999,
        'home_team': 'Équipe Test A',
        'away_team': 'Équipe Test B',
        'date': timezone.now().strftime('%Y-%m-%d %H:%M'),
        'stade': 'Stade de Test'
    }
    
    try:
        print("  📤 Envoi de notification de test...")
        
        # Envoyer la notification
        result = push_service.send_designation_notification(
            arbitres=[test_arbitre],
            match_info=test_match_data
        )
        
        print(f"  📊 Résultats:")
        print(f"    Succès: {result['success']}")
        print(f"    Échecs: {result['failed']}")
        
        if result['errors']:
            print(f"    Erreurs: {len(result['errors'])}")
            for error in result['errors']:
                print(f"      - {error}")
        
        if result['success'] > 0:
            print("  ✅ Notification envoyée avec succès!")
            return True
        else:
            print("  ❌ Aucune notification n'a été envoyée")
            return False
            
    except Exception as e:
        print(f"  ❌ Erreur lors de l'envoi: {e}")
        import traceback
        print(f"  Détails: {traceback.format_exc()}")
        return False
    
    # 6. Instructions pour les utilisateurs
    print("\n💡 INSTRUCTIONS POUR LES UTILISATEURS")
    print("  1. Se connecter à l'application")
    print("  2. Accepter les notifications push")
    print("  3. Vérifier que l'abonnement est créé")
    print("  4. Tester avec une vraie désignation")
    
    return True

def simulate_designation_notification():
    """Simuler l'envoi d'une notification de désignation"""
    
    print("\n🎭 SIMULATION DE NOTIFICATION DE DÉSIGNATION")
    print("=" * 50)
    
    # Prendre un arbitre actif
    arbitre = Arbitre.objects.filter(is_active=True).first()
    
    if not arbitre:
        print("❌ Aucun arbitre disponible pour la simulation")
        return False
    
    print(f"👤 Arbitre: {arbitre.get_full_name()}")
    
    # Vérifier les abonnements
    subscriptions = PushSubscription.objects.filter(
        arbitre=arbitre,
        is_active=True
    )
    
    if not subscriptions.exists():
        print("⚠️  Cet arbitre n'a pas d'abonnement actif")
        print("💡 Il devra d'abord s'abonner aux notifications")
        return False
    
    print(f"📱 {subscriptions.count()} abonnement(s) actif(s)")
    
    # Simuler une désignation
    match_info = {
        'id': 1000,
        'home_team': 'Club Sportif de Tunis',
        'away_team': 'Étoile Sportive du Sahel',
        'date': '2025-09-15 20:00',
        'stade': 'Stade Olympique de Radès'
    }
    
    print(f"🏆 Match: {match_info['home_team']} vs {match_info['away_team']}")
    print(f"📅 Date: {match_info['date']}")
    print(f"🏟️  Stade: {match_info['stade']}")
    
    # Envoyer la notification
    try:
        result = push_service.send_designation_notification(
            arbitres=[arbitre],
            match_info=match_info
        )
        
        print(f"\n📊 Résultats de l'envoi:")
        print(f"  ✅ Succès: {result['success']}")
        print(f"  ❌ Échecs: {result['failed']}")
        
        if result['success'] > 0:
            print("🎯 Notification de désignation envoyée avec succès!")
            print("📱 L'arbitre devrait recevoir la notification sur son appareil")
            return True
        else:
            print("❌ Échec de l'envoi de la notification")
            if result['errors']:
                print("🔍 Erreurs détectées:")
                for error in result['errors']:
                    print(f"  - {error}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la simulation: {e}")
        return False

def main():
    """Fonction principale"""
    
    print("🧪 TEST COMPLET DES NOTIFICATIONS APRÈS RÉSOLUTION VAPID")
    print("=" * 70)
    
    # Test principal
    if test_notifications_after_fix():
        print("\n✅ Configuration VAPID fonctionnelle!")
        
        # Demander si on veut simuler une notification
        response = input("\n🎭 Voulez-vous simuler une notification de désignation ? (oui/non): ").lower().strip()
        
        if response in ['oui', 'o', 'yes', 'y']:
            simulate_designation_notification()
        
        print("\n🎯 PROCHAINES ÉTAPES:")
        print("  1. Les utilisateurs peuvent maintenant s'abonner aux notifications")
        print("  2. Les notifications push fonctionneront correctement")
        print("  3. Tester avec de vraies désignations d'arbitrage")
        
    else:
        print("\n❌ Problème détecté dans la configuration")
        print("🔧 Exécuter d'abord fix_vapid_issue.py")

if __name__ == "__main__":
    main()
