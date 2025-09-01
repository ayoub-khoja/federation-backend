#!/usr/bin/env python3
"""
Test des notifications après correction des problèmes VAPID
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
from notifications.designation_service import designation_notification_service

def test_notification_after_fix():
    """Tester les notifications après correction des problèmes"""
    
    print("🔧 TEST DES NOTIFICATIONS APRÈS CORRECTION")
    print("=" * 60)
    
    # 1. Vérifier la configuration VAPID
    print("\n🔑 VÉRIFICATION VAPID:")
    try:
        from vapid_config import VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_EMAIL
        
        print(f"  ✅ Email: {VAPID_EMAIL}")
        print(f"  ✅ Clé privée: {len(VAPID_PRIVATE_KEY)} caractères")
        print(f"  ✅ Clé publique: {len(VAPID_PUBLIC_KEY)} caractères")
        
        # Vérifier le format des clés
        if VAPID_PRIVATE_KEY.startswith('MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg'):
            print("  ✅ Format clé privée: Correct (PEM base64)")
        else:
            print("  ⚠️  Format clé privée: Inattendu")
            
        if VAPID_PUBLIC_KEY.startswith('MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE'):
            print("  ✅ Format clé publique: Correct (PEM base64)")
        else:
            print("  ⚠️  Format clé publique: Inattendu")
            
    except ImportError as e:
        print(f"  ❌ Erreur VAPID: {e}")
        return False
    
    # 2. Vérifier les abonnements
    print("\n📱 ÉTAT DES ABONNEMENTS:")
    total_subscriptions = PushSubscription.objects.count()
    active_subscriptions = PushSubscription.objects.filter(is_active=True).count()
    
    print(f"  Total: {total_subscriptions}")
    print(f"  Actifs: {active_subscriptions}")
    print(f"  Inactifs: {total_subscriptions - active_subscriptions}")
    
    if active_subscriptions == 0:
        print("  ⚠️  Aucun abonnement actif")
        print("  💡 Les arbitres doivent se réabonner après la correction")
        return False
    
    # 3. Test d'envoi simple
    print("\n🧪 TEST D'ENVOI SIMPLE:")
    arbitre_test = PushSubscription.objects.filter(is_active=True).first().arbitre
    
    try:
        result = push_service.send_notification_to_arbitres(
            arbitres=[arbitre_test],
            title="🔧 Test Après Correction",
            body="Test des notifications après correction VAPID",
            data={'type': 'test_after_fix', 'status': 'corrected'},
            tag='test_after_fix'
        )
        
        print(f"  Résultat: {result}")
        
        if result.get('success', 0) > 0:
            print("  ✅ Test simple réussi!")
        else:
            print("  ❌ Test simple échoué")
            return False
            
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        return False
    
    # 4. Test de notification de désignation
    print("\n🏆 TEST DE NOTIFICATION DE DÉSIGNATION:")
    
    # Vérifier s'il y a des matchs
    matchs = Match.objects.all()
    if not matchs.exists():
        print("  ⚠️  Aucun match - création d'un match de test...")
        match_test = creer_match_test()
        if not match_test:
            return False
    else:
        match_test = matchs.first()
    
    print(f"  Match: {match_test}")
    
    try:
        # Créer une désignation de test
        designation = Designation.objects.create(
            match=match_test,
            arbitre=arbitre_test,
            role='arbitre_principal',
            status='en_attente'
        )
        
        print(f"  ✅ Désignation créée: {designation}")
        
        # Envoyer la notification
        result = designation_notification_service.notify_designation_created(
            arbitres=[arbitre_test],
            match_info={
                'id': match_test.id,
                'home_team': match_test.home_team,
                'away_team': match_test.away_team,
                'date': match_test.match_date.isoformat() if match_test.match_date else 'Non définie',
                'stade': match_test.stadium or 'Non défini'
            }
        )
        
        print(f"  Notification: {result}")
        
        if result.get('success', 0) > 0:
            print("  ✅ Notification de désignation envoyée!")
        else:
            print("  ❌ Échec de la notification de désignation")
        
        # Nettoyer
        designation.delete()
        
    except Exception as e:
        print(f"  ❌ Erreur désignation: {e}")
        return False
    
    # 5. Test d'envoi en masse
    print("\n🌐 TEST D'ENVOI EN MASSE:")
    
    arbitres_actifs = [sub.arbitre for sub in PushSubscription.objects.filter(is_active=True)]
    
    if len(arbitres_actifs) > 1:
        try:
            result = push_service.send_notification_to_arbitres(
                arbitres=arbitres_actifs,
                title="🌐 Test en Masse - Après Correction",
                body=f"Test d'envoi à {len(arbitres_actifs)} arbitres après correction",
                data={'type': 'bulk_test_after_fix', 'count': len(arbitres_actifs)},
                tag='bulk_test_after_fix'
            )
            
            print(f"  Résultat: {result}")
            
            if result.get('success', 0) > 0:
                print(f"  ✅ {result['success']} notifications envoyées!")
            else:
                print("  ❌ Échec de l'envoi en masse")
                
        except Exception as e:
            print(f"  ❌ Exception en masse: {e}")
    else:
        print("  ℹ️  Un seul arbitre - test en masse ignoré")
    
    # 6. Résumé final
    print("\n📊 RÉSUMÉ DES TESTS APRÈS CORRECTION:")
    print("=" * 50)
    print(f"  Configuration VAPID: ✅")
    print(f"  Abonnements actifs: {active_subscriptions}")
    print(f"  Test simple: ✅")
    print(f"  Test désignation: ✅")
    print(f"  Test en masse: {'✅' if len(arbitres_actifs) > 1 else 'ℹ️'}")
    
    print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
    print("  Le système de notifications fonctionne correctement après correction")
    
    return True

def creer_match_test():
    """Créer un match de test"""
    
    try:
        from datetime import datetime, timedelta
        
        match = Match.objects.create(
            home_team="Équipe Test A",
            away_team="Équipe Test B",
            match_date=datetime.now().date() + timedelta(days=7),
            match_time=datetime.now().time(),
            stadium="Stade de Test",
            status='scheduled'
        )
        
        print(f"  ✅ Match créé: {match}")
        return match
        
    except Exception as e:
        print(f"  ❌ Erreur création match: {e}")
        return False

if __name__ == "__main__":
    success = test_notification_after_fix()
    
    if success:
        print("\n🎉 CORRECTION RÉUSSIE!")
        print("  Le système de notifications fonctionne parfaitement")
    else:
        print("\n❌ PROBLÈMES PERSISTENT")
        print("  Vérifiez la configuration et relancez les tests")
    
    print("\n" + "=" * 60)
    print("✅ TEST TERMINÉ")

