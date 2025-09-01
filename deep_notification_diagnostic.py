#!/usr/bin/env python3
"""
Diagnostic approfondi du système de notifications push
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import Arbitre, PushSubscription
from matches.models import Designation, Match
from notifications.services import push_service

def deep_notification_diagnostic():
    """Diagnostic approfondi du système de notifications"""
    
    print("🔍 DIAGNOSTIC APPROFONDI DES NOTIFICATIONS")
    print("=" * 70)
    
    # 1. Vérification de l'environnement
    print("\n🌍 ENVIRONNEMENT:")
    print(f"  Python: {sys.version}")
    print(f"  Django: {django.get_version()}")
    print(f"  Répertoire: {os.getcwd()}")
    
    # 2. Configuration VAPID
    print("\n🔑 CONFIGURATION VAPID:")
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
        print(f"  ❌ Erreur import VAPID: {e}")
        return False
    
    # 3. Vérification de la base de données
    print("\n🗄️  BASE DE DONNÉES:")
    
    try:
        # Arbitres
        total_arbitres = Arbitre.objects.count()
        print(f"  ✅ Arbitres: {total_arbitres}")
        
        # Abonnements
        total_subscriptions = PushSubscription.objects.count()
        active_subscriptions = PushSubscription.objects.filter(is_active=True).count()
        print(f"  ✅ Abonnements: {total_subscriptions} (actifs: {active_subscriptions})")
        
        # Désignations
        total_designations = Designation.objects.count()
        print(f"  ✅ Désignations: {total_designations}")
        
        # Matchs
        total_matchs = Match.objects.count()
        print(f"  ✅ Matchs: {total_matchs}")
        
    except Exception as e:
        print(f"  ❌ Erreur base de données: {e}")
        return False
    
    # 4. Analyse des abonnements
    print("\n📱 ANALYSE DES ABONNEMENTS:")
    
    if active_subscriptions > 0:
        print(f"  📊 {active_subscriptions} abonnement(s) actif(s) trouvé(s)")
        
        for i, subscription in enumerate(PushSubscription.objects.filter(is_active=True)[:3], 1):
            print(f"\n  📱 Abonnement {i}:")
            print(f"     Arbitre: {subscription.arbitre.get_full_name()}")
            print(f"     Email: {subscription.arbitre.email}")
            print(f"     Endpoint: {subscription.endpoint[:80]}...")
            print(f"     Créé: {subscription.created_at}")
            print(f"     Dernière utilisation: {subscription.last_used or 'Jamais'}")
            
            # Analyser l'endpoint
            if 'fcm.googleapis.com' in subscription.endpoint:
                print(f"     Type: FCM (Firebase)")
            else:
                print(f"     Type: VAPID Standard")
                
    else:
        print("  ⚠️  Aucun abonnement actif")
    
    # 5. Test de connectivité
    print("\n🌐 TEST DE CONNECTIVITÉ:")
    
    try:
        # Test local
        response = requests.get('http://localhost:8000/api/', timeout=5)
        print(f"  ✅ Backend local: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Backend local: {e}")
    
    try:
        # Test frontend
        response = requests.get('http://localhost:3000', timeout=5)
        print(f"  ✅ Frontend local: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Frontend local: {e}")
    
    # 6. Test du service de notifications
    print("\n🧪 TEST DU SERVICE DE NOTIFICATIONS:")
    
    if active_subscriptions > 0:
        try:
            # Prendre le premier abonnement actif
            subscription = PushSubscription.objects.filter(is_active=True).first()
            arbitre = subscription.arbitre
            
            print(f"  Test avec: {arbitre.get_full_name()}")
            
            # Test d'envoi
            result = push_service.send_notification_to_arbitres(
                arbitres=[arbitre],
                title="🔍 Test de Diagnostic",
                body="Test approfondi du système de notifications",
                data={
                    'type': 'deep_diagnostic',
                    'timestamp': datetime.now().isoformat(),
                    'test_id': 'deep_diagnostic_001'
                },
                tag='deep_diagnostic'
            )
            
            print(f"  Résultat: {result}")
            
            if result.get('success', 0) > 0:
                print("  ✅ Test du service réussi!")
            else:
                print("  ❌ Test du service échoué")
                if result.get('errors'):
                    print(f"  Erreurs: {result['errors']}")
                    
        except Exception as e:
            print(f"  ❌ Exception lors du test: {e}")
            import traceback
            print(f"  Stack trace: {traceback.format_exc()}")
    else:
        print("  ⚠️  Impossible de tester - aucun abonnement actif")
    
    # 7. Vérification des modèles
    print("\n📋 VÉRIFICATION DES MODÈLES:")
    
    try:
        # Vérifier PushSubscription
        subscription_fields = [f.name for f in PushSubscription._meta.get_fields()]
        required_fields = ['endpoint', 'p256dh', 'auth', 'arbitre', 'is_active']
        
        for field in required_fields:
            if field in subscription_fields:
                print(f"  ✅ PushSubscription.{field}")
            else:
                print(f"  ❌ PushSubscription.{field} manquant")
        
        # Vérifier Arbitre
        arbitre_fields = [f.name for f in Arbitre._meta.get_fields()]
        required_arbitre_fields = ['user', 'grade', 'ligue_arbitrage']
        
        for field in required_arbitre_fields:
            if field in arbitre_fields:
                print(f"  ✅ Arbitre.{field}")
            else:
                print(f"  ❌ Arbitre.{field} manquant")
                
    except Exception as e:
        print(f"  ❌ Erreur vérification modèles: {e}")
    
    # 8. Recommandations
    print("\n💡 RECOMMANDATIONS:")
    
    if active_subscriptions == 0:
        print("  1. Les arbitres doivent s'abonner aux notifications")
        print("  2. Vérifier que le frontend fonctionne")
        print("  3. Vérifier les permissions du navigateur")
    
    if total_subscriptions > 0 and active_subscriptions == 0:
        print("  1. Réactiver les abonnements existants")
        print("  2. Vérifier la validité des endpoints")
    
    print("  3. Vérifier la configuration VAPID")
    print("  4. Tester avec un navigateur supportant les notifications")
    print("  5. Vérifier la console du navigateur pour les erreurs")
    
    # 9. Résumé final
    print("\n📊 RÉSUMÉ DU DIAGNOSTIC:")
    print("=" * 50)
    
    status_vapid = 'VAPID_PRIVATE_KEY' in locals()
    status_db = 'total_arbitres' in locals()
    status_service = 'result' in locals() and result.get('success', 0) > 0 if 'result' in locals() else False
    
    print(f"  Configuration VAPID: {'✅' if status_vapid else '❌'}")
    print(f"  Base de données: {'✅' if status_db else '❌'}")
    print(f"  Service notifications: {'✅' if status_service else '❌'}")
    print(f"  Abonnements actifs: {active_subscriptions}")
    
    overall_status = status_vapid and status_db and (active_subscriptions > 0)
    
    if overall_status:
        print("\n🎉 SYSTÈME PRÊT!")
        print("  Les notifications devraient fonctionner correctement")
    else:
        print("\n⚠️  PROBLÈMES DÉTECTÉS")
        print("  Vérifiez les points mentionnés ci-dessus")
    
    return overall_status

if __name__ == "__main__":
    success = deep_notification_diagnostic()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ DIAGNOSTIC TERMINÉ - SYSTÈME PRÊT")
    else:
        print("❌ DIAGNOSTIC TERMINÉ - PROBLÈMES DÉTECTÉS")
    
    sys.exit(0 if success else 1)

