#!/usr/bin/env python3
"""
Script pour tester les notifications lors de la création d'une désignation d'arbitrage
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import Arbitre, PushSubscription
from matches.models import Match, Designation
from notifications.services import push_service
from django.utils import timezone

def test_designation_notifications():
    """Tester les notifications lors de la création d'une désignation"""
    
    print("🏆 TEST DES NOTIFICATIONS DE DÉSIGNATION")
    print("=" * 60)
    
    # 1. Vérifier la configuration VAPID
    print("\n🔑 VÉRIFICATION VAPID")
    try:
        from vapid_config import VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY
        print(f"  ✅ Clés VAPID configurées")
        print(f"  🔐 Privée: {len(VAPID_PRIVATE_KEY)} caractères")
        print(f"  🔓 Publique: {len(VAPID_PUBLIC_KEY)} caractères")
    except ImportError:
        print("  ❌ Configuration VAPID manquante")
        return False
    
    # 2. Vérifier les arbitres disponibles
    print("\n👥 ARBITRES DISPONIBLES")
    arbitres = Arbitre.objects.filter(is_active=True)
    total_arbitres = arbitres.count()
    
    if total_arbitres == 0:
        print("  ❌ Aucun arbitre actif trouvé")
        return False
    
    print(f"  📊 Total arbitres actifs: {total_arbitres}")
    
    # Afficher les arbitres avec leurs abonnements
    for i, arbitre in enumerate(arbitres[:5], 1):  # Limiter à 5 pour l'affichage
        subscriptions = PushSubscription.objects.filter(
            arbitre=arbitre,
            is_active=True
        ).count()
        status = "✅" if subscriptions > 0 else "⚠️"
        print(f"    {i}. {arbitre.get_full_name()} - {subscriptions} abonnement(s) {status}")
    
    if total_arbitres > 5:
        print(f"    ... et {total_arbitres - 5} autres arbitres")
    
    # 3. Vérifier les matches disponibles
    print("\n⚽ MATCHES DISPONIBLES")
    matches = Match.objects.filter(
        match_date__gte=timezone.now().date() - timedelta(days=30),
        match_date__lte=timezone.now().date() + timedelta(days=90)
    ).order_by('match_date')
    
    total_matches = matches.count()
    
    if total_matches == 0:
        print("  ℹ️  Aucun match récent trouvé")
        print("  💡 Créer d'abord un match pour tester")
        return False
    
    print(f"  📊 Total matches: {total_matches}")
    
    # Afficher quelques matches
    for i, match in enumerate(matches[:3], 1):
        designation_count = Designation.objects.filter(match=match).count()
        status = "🏆" if designation_count > 0 else "⏳"
        print(f"    {i}. {match.home_team} vs {match.away_team}")
        print(f"       📅 {match.match_date.strftime('%Y-%m-%d')}")
        print(f"       🏟️  {match.stadium}")
        print(f"       {status} {designation_count} désignation(s)")
    
    # 4. Créer une désignation de test
    print("\n🎭 CRÉATION D'UNE DÉSIGNATION DE TEST")
    
    # Prendre le premier match sans désignation
    match_sans_designation = matches.filter(designation__isnull=True).first()
    
    if not match_sans_designation:
        print("  ℹ️  Tous les matches ont déjà des désignations")
        print("  💡 Créer un nouveau match ou utiliser un match existant")
        
        # Demander si on veut utiliser un match existant
        response = input("  ❓ Utiliser un match existant ? (oui/non): ").lower().strip()
        if response in ['oui', 'o', 'yes', 'y']:
            match_sans_designation = matches.first()
        else:
            return False
    
    print(f"  🏆 Match sélectionné: {match_sans_designation.home_team} vs {match_sans_designation.away_team}")
    
    # 5. Sélectionner des arbitres pour la désignation
    print("\n👨‍⚖️  SÉLECTION DES ARBITRES")
    
    # Prendre 3 arbitres avec des abonnements actifs
    arbitres_avec_abonnements = []
    for arbitre in arbitres:
        if PushSubscription.objects.filter(arbitre=arbitre, is_active=True).exists():
            arbitres_avec_abonnements.append(arbitre)
            if len(arbitres_avec_abonnements) >= 3:
                break
    
    if not arbitres_avec_abonnements:
        print("  ⚠️  Aucun arbitre avec abonnement actif trouvé")
        print("  💡 Les arbitres devront d'abord s'abonner aux notifications")
        return False
    
    print(f"  📱 {len(arbitres_avec_abonnements)} arbitre(s) avec abonnement(s) sélectionné(s)")
    
    for i, arbitre in enumerate(arbitres_avec_abonnements, 1):
        print(f"    {i}. {arbitre.get_full_name()} ({arbitre.grade})")
    
    # 6. Créer la désignation
    print("\n🚀 CRÉATION DE LA DÉSIGNATION")
    
    try:
        # Créer la désignation
        designation = Designation.objects.create(
            match=match_sans_designation,
            arbitre_principal=arbitres_avec_abonnements[0] if len(arbitres_avec_abonnements) > 0 else None,
            arbitre_assistant1=arbitres_avec_abonnements[1] if len(arbitres_avec_abonnements) > 1 else None,
            arbitre_assistant2=arbitres_avec_abonnements[2] if len(arbitres_avec_abonnements) > 2 else None,
            date_designation=timezone.now(),
            statut='confirmée'
        )
        
        print(f"  ✅ Désignation créée avec l'ID: {designation.id}")
        
    except Exception as e:
        print(f"  ❌ Erreur lors de la création de la désignation: {e}")
        return False
    
    # 7. Envoyer les notifications
    print("\n🔔 ENVOI DES NOTIFICATIONS")
    
    # Préparer les données du match
    match_info = {
        'id': match_sans_designation.id,
        'home_team': match_sans_designation.home_team,
        'away_team': match_sans_designation.away_team,
        'date': match_sans_designation.match_date.strftime('%Y-%m-%d'),
        'stade': match_sans_designation.stadium
    }
    
    try:
        # Envoyer les notifications
        result = push_service.send_designation_notification(
            arbitres=arbitres_avec_abonnements,
            match_info=match_info
        )
        
        print(f"  📊 Résultats de l'envoi:")
        print(f"    ✅ Succès: {result['success']}")
        print(f"    ❌ Échecs: {result['failed']}")
        
        if result['errors']:
            print(f"    🔍 Erreurs: {len(result['errors'])}")
            for error in result['errors']:
                print(f"      - {error}")
        
        if result['success'] > 0:
            print("  🎯 Notifications envoyées avec succès!")
            print("  📱 Les arbitres devraient recevoir les notifications")
            
            # Afficher les détails
            print(f"\n📋 DÉTAILS DE LA DÉSIGNATION:")
            print(f"  🏆 Match: {match_info['home_team']} vs {match_info['away_team']}")
            print(f"  📅 Date: {match_info['date']}")
            print(f"  🏟️  Stade: {match_info['stade']}")
            print(f"  👨‍⚖️  Arbitres notifiés: {len(arbitres_avec_abonnements)}")
            
            return True
        else:
            print("  ❌ Aucune notification n'a été envoyée")
            return False
            
    except Exception as e:
        print(f"  ❌ Erreur lors de l'envoi des notifications: {e}")
        import traceback
        print(f"  Détails: {traceback.format_exc()}")
        return False

def cleanup_test_designation():
    """Nettoyer la désignation de test"""
    print("\n🧹 NETTOYAGE DE LA DÉSIGNATION DE TEST")
    
    try:
        # Supprimer la désignation de test (ID 999 ou similaire)
        test_designations = Designation.objects.filter(
            match__home_team__icontains='Test',
            match__away_team__icontains='Test'
        )
        
        if test_designations.exists():
            count = test_designations.count()
            test_designations.delete()
            print(f"  ✅ {count} désignation(s) de test supprimée(s)")
        else:
            print("  ℹ️  Aucune désignation de test à supprimer")
            
    except Exception as e:
        print(f"  ❌ Erreur lors du nettoyage: {e}")

def main():
    """Fonction principale"""
    
    print("🏆 TEST COMPLET DES NOTIFICATIONS DE DÉSIGNATION")
    print("=" * 70)
    
    # Test principal
    if test_designation_notifications():
        print("\n✅ Test des notifications de désignation réussi!")
        print("\n💡 PROCHAINES ÉTAPES:")
        print("  1. Vérifier que les arbitres ont reçu les notifications")
        print("  2. Tester avec de vraies désignations")
        print("  3. Les notifications fonctionnent maintenant correctement")
        
        # Demander si on veut nettoyer
        response = input("\n🧹 Voulez-vous nettoyer les données de test ? (oui/non): ").lower().strip()
        if response in ['oui', 'o', 'yes', 'y']:
            cleanup_test_designation()
        
    else:
        print("\n❌ Test des notifications de désignation échoué")
        print("🔧 Vérifier la configuration VAPID et les abonnements")

if __name__ == "__main__":
    main()


