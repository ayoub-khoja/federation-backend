#!/usr/bin/env python3
"""
Script pour tester la création d'une vraie désignation et vérifier les notifications
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import Arbitre
from matches.models import Match, Designation
from django.utils import timezone
from datetime import timedelta

def test_real_designation_creation():
    """Tester la création d'une vraie désignation avec notifications"""
    
    print("🏆 TEST DE CRÉATION D'UNE VRAIE DÉSIGNATION")
    print("=" * 60)
    
    # 1. Vérifier l'arbitre avec abonnement
    print("\n👤 ARBITRE AVEC ABONNEMENT")
    
    try:
        arbitre = Arbitre.objects.get(id=14)  # hhhh rrrrr
        print(f"✅ Arbitre: {arbitre.get_full_name()} (ID: {arbitre.id})")
        
        # Vérifier son abonnement
        from accounts.models import PushSubscription
        subs = PushSubscription.objects.filter(arbitre=arbitre, is_active=True)
        if subs.exists():
            print(f"📱 Abonnement actif: OUI")
            print(f"   Endpoint: {subs.first().endpoint[:50]}...")
        else:
            print("❌ Pas d'abonnement actif")
            return False
            
    except Arbitre.DoesNotExist:
        print("❌ Arbitre ID 14 non trouvé")
        return False
    
    # 2. Créer un match de test
    print("\n⚽ CRÉATION D'UN MATCH DE TEST")
    
    match_date = timezone.now().date() + timedelta(days=7)
    match_time = timezone.now().time()
    
    try:
        match = Match.objects.create(
            home_team="Équipe Test A",
            away_team="Équipe Test B",
            match_date=match_date,
            match_time=match_time,
            stadium="Stade de Test",
            match_type="championnat",
            category="senior",
            status="scheduled",
            referee=arbitre
        )
        
        print(f"✅ Match créé: {match.home_team} vs {match.away_team}")
        print(f"     📅 Date: {match.match_date}")
        print(f"     🏟️  Stade: {match.stadium}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du match: {e}")
        return False
    
    # 3. Créer une désignation (cela devrait déclencher le signal automatique)
    print("\n🎭 CRÉATION DE LA DÉSIGNATION (NOTIFICATION AUTOMATIQUE)")
    
    try:
        designation = Designation.objects.create(
            match=match,
            arbitre=arbitre,
            date_designation=timezone.now(),
            status='proposed'
        )
        
        print(f"✅ Désignation créée avec l'ID: {designation.id}")
        print(f"     👨‍⚖️  Arbitre: {designation.arbitre.get_full_name()}")
        print(f"     🏆 Match: {designation.match}")
        print(f"     📊 Statut: {designation.get_status_display()}")
        
        # Vérifier si la notification a été marquée comme envoyée
        designation.refresh_from_db()
        if hasattr(designation, 'notification_envoyee'):
            print(f"     📱 Notification envoyée: {designation.notification_envoyee}")
        else:
            print(f"     📱 Pas de champ notification_envoyee")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de la désignation: {e}")
        return False
    
    # 4. Attendre un peu pour la notification
    print("\n⏳ ATTENTE DE LA NOTIFICATION...")
    print("💡 Vérifiez votre navigateur pour voir la notification push !")
    
    # 5. Vérifier l'état final
    print("\n🔍 VÉRIFICATION FINALE")
    
    designation.refresh_from_db()
    
    print(f"📊 Désignation ID: {designation.id}")
    print(f"👨‍⚖️  Arbitre: {designation.arbitre.get_full_name()}")
    print(f"🏆 Match: {designation.match}")
    print(f"📊 Statut: {designation.get_status_display()}")
    
    # 6. Nettoyer les données de test
    print("\n🧹 NETTOYAGE DES DONNÉES DE TEST")
    
    try:
        # Supprimer la désignation
        designation.delete()
        print("✅ Désignation supprimée")
        
        # Supprimer le match
        match.delete()
        print("✅ Match supprimé")
        
    except Exception as e:
        print(f"❌ Erreur lors du nettoyage: {e}")
    
    print("\n🎯 TEST TERMINÉ!")
    print("💡 Si vous avez reçu une notification, tout fonctionne parfaitement!")
    print("   Sinon, il y a encore un problème à résoudre.")
    
    return True

if __name__ == "__main__":
    success = test_real_designation_creation()
    sys.exit(0 if success else 1)
