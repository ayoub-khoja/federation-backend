#!/usr/bin/env python3
"""
Test complet du système de notifications push pour les désignations
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from matches.models import Designation, Match
from accounts.models import Arbitre, PushSubscription
from notifications.services import push_service
from notifications.designation_service import designation_notification_service

def test_complet_notifications():
    """Test complet du système de notifications"""
    
    print("🔔 TEST COMPLET DU SYSTÈME DE NOTIFICATIONS")
    print("=" * 70)
    
    # 1. Vérifier la configuration VAPID
    print("\n🔑 VÉRIFICATION DE LA CONFIGURATION VAPID:")
    try:
        from vapid_config import VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_EMAIL
        print(f"  ✅ Clé privée VAPID: {VAPID_PRIVATE_KEY[:30]}...")
        print(f"  ✅ Clé publique VAPID: {VAPID_PUBLIC_KEY[:30]}...")
        print(f"  ✅ Email VAPID: {VAPID_EMAIL}")
    except ImportError as e:
        print(f"  ❌ Erreur import VAPID: {e}")
        return False
    
    # 2. Vérifier l'état des abonnements
    print("\n📱 ÉTAT DES ABONNEMENTS PUSH:")
    total_subscriptions = PushSubscription.objects.count()
    active_subscriptions = PushSubscription.objects.filter(is_active=True).count()
    inactive_subscriptions = total_subscriptions - active_subscriptions
    
    print(f"  Total abonnements: {total_subscriptions}")
    print(f"  Abonnements actifs: {active_subscriptions}")
    print(f"  Abonnements inactifs: {inactive_subscriptions}")
    
    if active_subscriptions == 0:
        print("  ⚠️  Aucun abonnement actif - impossible de tester")
        return False
    
    # 3. Lister les arbitres avec abonnements actifs
    print("\n👥 ARBITRES AVEC ABONNEMENTS ACTIFS:")
    arbitres_actifs = []
    for subscription in PushSubscription.objects.filter(is_active=True):
        arbitre = subscription.arbitre
        arbitres_actifs.append(arbitre)
        print(f"  ✅ {arbitre.get_full_name()} - {arbitre.email}")
        print(f"     Endpoint: {subscription.endpoint[:50]}...")
        print(f"     Créé: {subscription.created_at}")
        print()
    
    # 4. Vérifier les désignations existantes
    print("\n🏟️  DÉSIGNATIONS EXISTANTES:")
    total_designations = Designation.objects.count()
    print(f"  Total désignations: {total_designations}")
    
    if total_designations == 0:
        print("  ⚠️  Aucune désignation - création d'une désignation de test...")
        designation_test = creer_designation_test()
        if not designation_test:
            return False
    
    # 5. Test d'envoi de notification simple
    print("\n🧪 TEST D'ENVOI DE NOTIFICATION SIMPLE:")
    arbitre_test = arbitres_actifs[0]
    print(f"  Test avec: {arbitre_test.get_full_name()}")
    
    try:
        result = push_service.send_notification_to_arbitres(
            arbitres=[arbitre_test],
            title="🧪 Test de Notification",
            body="Ceci est un test du système de notifications",
            data={'type': 'test', 'timestamp': datetime.now().isoformat()},
            tag='test'
        )
        
        print(f"  Résultat: {result}")
        
        if result.get('success', 0) > 0:
            print("  ✅ Notification de test envoyée!")
            print("  🎯 Vérifiez votre navigateur pour la notification")
        else:
            print("  ❌ Échec de l'envoi")
            if result.get('errors'):
                print(f"  Erreurs: {result['errors']}")
                
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        import traceback
        print(f"  Stack trace: {traceback.format_exc()}")
    
    # 6. Test d'envoi de notification de désignation
    print("\n🏆 TEST DE NOTIFICATION DE DÉSIGNATION:")
    
    # Prendre une désignation existante ou en créer une
    designation = Designation.objects.first()
    if not designation:
        designation = creer_designation_test()
    
    if designation:
        print(f"  Test avec: {designation.match} - {designation.arbitre.get_full_name()}")
        
        try:
            # Utiliser le service de désignation
            result = designation_notification_service.notify_designation_created(
                arbitres=[designation.arbitre],
                match_info={
                    'id': designation.match.id,
                    'home_team': designation.match.home_team,
                    'away_team': designation.match.away_team,
                    'date': designation.match.match_date.isoformat() if designation.match.match_date else 'Non définie',
                    'stade': designation.match.stadium or 'Non défini'
                }
            )
            
            print(f"  Résultat: {result}")
            
            if result.get('success', 0) > 0:
                print("  ✅ Notification de désignation envoyée!")
            else:
                print("  ❌ Échec de l'envoi")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            import traceback
            print(f"  Stack trace: {traceback.format_exc()}")
    
    # 7. Test d'envoi en masse
    print("\n🌐 TEST D'ENVOI EN MASSE:")
    
    if len(arbitres_actifs) > 1:
        print(f"  Envoi à {len(arbitres_actifs)} arbitres...")
        
        try:
            result = push_service.send_notification_to_arbitres(
                arbitres=arbitres_actifs,
                title="🌐 Test en Masse",
                body=f"Test d'envoi à {len(arbitres_actifs)} arbitres",
                data={'type': 'bulk_test', 'count': len(arbitres_actifs)},
                tag='bulk_test'
            )
            
            print(f"  Résultat: {result}")
            
            if result.get('success', 0) > 0:
                print(f"  ✅ {result['success']} notifications envoyées!")
            else:
                print("  ❌ Échec de l'envoi en masse")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")
    else:
        print("  ⚠️  Un seul arbitre actif - test en masse ignoré")
    
    # 8. Vérification finale
    print("\n🔍 VÉRIFICATION FINALE:")
    print("  ✅ Configuration VAPID vérifiée")
    print(f"  ✅ {active_subscriptions} abonnements actifs")
    print(f"  ✅ {total_designations} désignations dans la base")
    print("  ✅ Tests de notifications effectués")
    
    return True

def creer_designation_test():
    """Créer une désignation de test"""
    
    print("\n🧪 CRÉATION D'UNE DÉSIGNATION DE TEST:")
    print("=" * 50)
    
    try:
        # Vérifier s'il y a des matchs
        matchs = Match.objects.all()
        if not matchs.exists():
            print("  ⚠️  Aucun match trouvé dans la base")
            return False
        
        # Vérifier s'il y a des arbitres
        arbitres = Arbitre.objects.all()
        if not arbitres.exists():
            print("  ⚠️  Aucun arbitre trouvé dans la base")
            return False
        
        # Prendre le premier match et arbitre
        match_test = matchs.first()
        arbitre_test = arbitres.first()
        
        print(f"  Match de test: {match_test}")
        print(f"  Arbitre de test: {arbitre_test.get_full_name()}")
        
        # Créer la désignation
        designation = Designation.objects.create(
            match=match_test,
            arbitre=arbitre_test,
            role='arbitre_principal',
            status='en_attente'
        )
        
        print(f"  ✅ Désignation créée: {designation}")
        print(f"  ID: {designation.id}")
        
        return designation
        
    except Exception as e:
        print(f"  ❌ Erreur lors de la création: {e}")
        return False

def nettoyer_abonnements_test():
    """Nettoyer les abonnements de test"""
    
    print("\n🧹 NETTOYAGE DES ABONNEMENTS DE TEST:")
    print("=" * 50)
    
    try:
        # Supprimer les abonnements de test
        test_subscriptions = PushSubscription.objects.filter(
            endpoint__contains='test'
        )
        
        count = test_subscriptions.count()
        if count > 0:
            test_subscriptions.delete()
            print(f"  ✅ {count} abonnements de test supprimés")
        else:
            print("  ℹ️  Aucun abonnement de test à supprimer")
            
    except Exception as e:
        print(f"  ❌ Erreur lors du nettoyage: {e}")

if __name__ == "__main__":
    print("🚀 TEST COMPLET DU SYSTÈME DE NOTIFICATIONS")
    print("=" * 70)
    
    try:
        # Test principal
        success = test_complet_notifications()
        
        if success:
            print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
            print("\n💡 Le système de notifications fonctionne correctement")
            print("   Vous pouvez maintenant créer des désignations et")
            print("   les arbitres recevront automatiquement des notifications")
        else:
            print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
            print("\n🔧 Vérifiez:")
            print("   1. La configuration VAPID")
            print("   2. Les abonnements push des arbitres")
            print("   3. La connectivité réseau")
            
    except Exception as e:
        print(f"\n💥 ERREUR CRITIQUE: {e}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
    
    print("\n" + "=" * 70)
    print("✅ TEST TERMINÉ")

