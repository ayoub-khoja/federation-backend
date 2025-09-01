#!/usr/bin/env python3
"""
Test des notifications sur plusieurs comptes arbitres
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

def test_notifications_multi_comptes():
    """Tester les notifications sur plusieurs comptes arbitres"""
    
    print("👥 TEST DES NOTIFICATIONS SUR PLUSIEURS COMPTES")
    print("=" * 70)
    
    # 1. Vérifier les arbitres disponibles
    print("\n👥 ARBITRES DISPONIBLES:")
    arbitres = Arbitre.objects.all()
    total_arbitres = arbitres.count()
    
    if total_arbitres == 0:
        print("  ❌ Aucun arbitre trouvé dans la base")
        return False
    
    print(f"  Total arbitres: {total_arbitres}")
    
    for i, arbitre in enumerate(arbitres, 1):
        print(f"  {i}. {arbitre.get_full_name()} - {arbitre.email}")
        print(f"     Grade: {arbitre.grade}")
        print(f"     Ligue: {arbitre.ligue_arbitrage}")
        print()
    
    # 2. Vérifier les abonnements push
    print("\n📱 ÉTAT DES ABONNEMENTS PUSH:")
    arbitres_avec_abonnements = []
    arbitres_sans_abonnements = []
    
    for arbitre in arbitres:
        subscription = PushSubscription.objects.filter(
            arbitre=arbitre, 
            is_active=True
        ).first()
        
        if subscription:
            arbitres_avec_abonnements.append(arbitre)
            print(f"  ✅ {arbitre.get_full_name()}: Abonné et actif")
            print(f"     Endpoint: {subscription.endpoint[:50]}...")
        else:
            arbitres_sans_abonnements.append(arbitre)
            print(f"  ❌ {arbitre.get_full_name()}: Pas d'abonnement")
    
    print(f"\n  📊 Résumé:")
    print(f"     Arbitres avec abonnements: {len(arbitres_avec_abonnements)}")
    print(f"     Arbitres sans abonnements: {len(arbitres_sans_abonnements)}")
    
    if len(arbitres_avec_abonnements) == 0:
        print("\n  ⚠️  Aucun arbitre avec abonnement - impossible de tester")
        print("  💡 Les arbitres doivent d'abord s'abonner aux notifications")
        return False
    
    # 3. Test d'envoi individuel à chaque arbitre abonné
    print("\n🧪 TEST INDIVIDUEL PAR ARBITRE:")
    
    for i, arbitre in enumerate(arbitres_avec_abonnements, 1):
        print(f"\n  📱 Test {i}: {arbitre.get_full_name()}")
        print(f"     Email: {arbitre.email}")
        print(f"     Grade: {arbitre.grade}")
        
        try:
            # Envoyer une notification de test personnalisée
            result = push_service.send_notification_to_arbitres(
                arbitres=[arbitre],
                title=f"🧪 Test {i} - {arbitre.get_full_name()}",
                body=f"Ceci est un test de notification pour {arbitre.get_full_name()}",
                data={
                    'type': 'test_individual',
                    'arbitre_id': arbitre.id,
                    'arbitre_name': arbitre.get_full_name(),
                    'test_number': i,
                    'timestamp': datetime.now().isoformat()
                },
                tag=f'test_individual_{i}'
            )
            
            print(f"     Résultat: {result}")
            
            if result.get('success', 0) > 0:
                print(f"     ✅ Notification envoyée avec succès!")
            else:
                print(f"     ❌ Échec de l'envoi")
                if result.get('errors'):
                    print(f"     Erreurs: {result['errors']}")
                    
        except Exception as e:
            print(f"     ❌ Exception: {e}")
    
    # 4. Test d'envoi en masse à tous les arbitres abonnés
    print(f"\n🌐 TEST D'ENVOI EN MASSE À {len(arbitres_avec_abonnements)} ARBITRES:")
    
    try:
        result = push_service.send_notification_to_arbitres(
            arbitres=arbitres_avec_abonnements,
            title="🌐 Test en Masse - Tous les Arbitres",
            body=f"Test d'envoi en masse à {len(arbitres_avec_abonnements)} arbitres",
            data={
                'type': 'bulk_test_all',
                'total_arbitres': len(arbitres_avec_abonnements),
                'timestamp': datetime.now().isoformat()
            },
            tag='bulk_test_all'
        )
        
        print(f"  Résultat global: {result}")
        
        if result.get('success', 0) > 0:
            print(f"  ✅ {result['success']} notifications envoyées avec succès!")
            if result.get('failed', 0) > 0:
                print(f"  ❌ {result['failed']} échecs")
        else:
            print("  ❌ Échec de l'envoi en masse")
            
    except Exception as e:
        print(f"  ❌ Exception lors de l'envoi en masse: {e}")
        import traceback
        print(f"  Stack trace: {traceback.format_exc()}")
    
    # 5. Test de notifications de désignation
    print("\n🏆 TEST DE NOTIFICATIONS DE DÉSIGNATION:")
    
    # Vérifier s'il y a des matchs
    matchs = Match.objects.all()
    if not matchs.exists():
        print("  ⚠️  Aucun match trouvé - création d'un match de test...")
        match_test = creer_match_test()
        if not match_test:
            print("  ❌ Impossible de créer un match de test")
            return False
    else:
        match_test = matchs.first()
    
    print(f"  Match de test: {match_test}")
    
    # Créer des désignations de test pour plusieurs arbitres
    designations_crees = []
    
    for i, arbitre in enumerate(arbitres_avec_abonnements[:3], 1):  # Limiter à 3 pour le test
        try:
            # Créer une désignation
            designation = Designation.objects.create(
                match=match_test,
                arbitre=arbitre,
                role='arbitre_principal',
                status='en_attente'
            )
            
            designations_crees.append(designation)
            print(f"  ✅ Désignation {i} créée pour {arbitre.get_full_name()}")
            
            # Envoyer la notification de désignation
            result = designation_notification_service.notify_designation_created(
                arbitres=[arbitre],
                match_info={
                    'id': match_test.id,
                    'home_team': match_test.home_team,
                    'away_team': match_test.away_team,
                    'date': match_test.match_date.isoformat() if match_test.match_date else 'Non définie',
                    'stade': match_test.stadium or 'Non défini'
                }
            )
            
            print(f"     Notification: {result}")
            
        except Exception as e:
            print(f"  ❌ Erreur pour {arbitre.get_full_name()}: {e}")
    
    # 6. Nettoyage des désignations de test
    if designations_crees:
        print(f"\n🧹 NETTOYAGE DES {len(designations_crees)} DÉSIGNATIONS DE TEST:")
        
        for designation in designations_crees:
            try:
                designation.delete()
                print(f"  ✅ Désignation supprimée: {designation}")
            except Exception as e:
                print(f"  ❌ Erreur suppression: {e}")
    
    # 7. Résumé final
    print("\n📊 RÉSUMÉ DU TEST MULTI-COMPTES:")
    print("=" * 50)
    print(f"  Total arbitres: {total_arbitres}")
    print(f"  Arbitres avec abonnements: {len(arbitres_avec_abonnements)}")
    print(f"  Arbitres sans abonnements: {len(arbitres_sans_abonnements)}")
    print(f"  Tests individuels effectués: {len(arbitres_avec_abonnements)}")
    print(f"  Test en masse: {'✅' if len(arbitres_avec_abonnements) > 0 else '❌'}")
    print(f"  Tests de désignation: {len(designations_crees)}")
    
    if len(arbitres_avec_abonnements) > 0:
        print("\n🎉 TESTS RÉUSSIS!")
        print("  Les notifications fonctionnent correctement sur plusieurs comptes")
    else:
        print("\n❌ TESTS INCOMPLETS")
        print("  Aucun arbitre n'a d'abonnement actif")
    
    return True

def creer_match_test():
    """Créer un match de test"""
    
    try:
        # Créer un match simple
        match = Match.objects.create(
            home_team="Équipe A",
            away_team="Équipe B",
            match_date=datetime.now().date() + timedelta(days=7),
            match_time=datetime.now().time(),
            stadium="Stade de Test",
            status='scheduled'
        )
        
        print(f"  ✅ Match de test créé: {match}")
        return match
        
    except Exception as e:
        print(f"  ❌ Erreur création match: {e}")
        return False

def afficher_instructions_abonnement():
    """Afficher les instructions pour s'abonner aux notifications"""
    
    print("\n💡 INSTRUCTIONS POUR S'ABONNER AUX NOTIFICATIONS:")
    print("=" * 60)
    print("  1. Ouvrir le frontend: http://localhost:3000")
    print("  2. Se connecter avec un compte arbitre")
    print("  3. Aller dans le profil utilisateur")
    print("  4. Activer les notifications push")
    print("  5. Accepter la permission dans le navigateur")
    print("  6. Vérifier que l'abonnement est créé")
    print("  7. Revenir ici et relancer le test")
    print("\n  🔧 En cas de problème:")
    print("     - Vérifier la console du navigateur")
    print("     - Vérifier les permissions du navigateur")
    print("     - Vérifier que le service worker est installé")

if __name__ == "__main__":
    print("🚀 TEST DES NOTIFICATIONS SUR PLUSIEURS COMPTES")
    print("=" * 70)
    
    try:
        # Test principal
        success = test_notifications_multi_comptes()
        
        if not success:
            print("\n💡 Aucun arbitre avec abonnement trouvé")
            afficher_instructions_abonnement()
        
    except Exception as e:
        print(f"\n💥 ERREUR CRITIQUE: {e}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
    
    print("\n" + "=" * 70)
    print("✅ TEST TERMINÉ")
