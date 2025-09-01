#!/usr/bin/env python3
"""
Script pour tester la création d'une désignation via l'admin Django
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

def test_admin_designation():
    """Tester la création d'une désignation via l'admin"""
    
    print("🏆 TEST DE CRÉATION VIA L'ADMIN DJANGO")
    print("=" * 50)
    
    # 1. Vérifier l'arbitre
    try:
        arbitre = Arbitre.objects.get(id=14)  # hhhh rrrrr
        print(f"👤 Arbitre: {arbitre.get_full_name()} (ID: {arbitre.id})")
        
        # Vérifier son abonnement
        from accounts.models import PushSubscription
        subs = PushSubscription.objects.filter(arbitre=arbitre, is_active=True)
        if subs.exists():
            print(f"📱 Abonnement actif: OUI")
        else:
            print("❌ Pas d'abonnement actif")
            return False
            
    except Arbitre.DoesNotExist:
        print("❌ Arbitre ID 14 non trouvé")
        return False
    
    # 2. Créer un match via l'admin (simulation)
    print("\n⚽ CRÉATION D'UN MATCH VIA L'ADMIN")
    
    match_date = timezone.now().date() + timedelta(days=14)
    match_time = timezone.now().time()
    
    try:
        match = Match.objects.create(
            home_team="Club Africain",
            away_team="Étoile du Sahel",
            match_date=match_date,
            match_time=match_time,
            stadium="Stade Olympique de Radès",
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
    
    # 3. Créer une désignation via l'admin (simulation)
    print("\n🎭 CRÉATION DE LA DÉSIGNATION VIA L'ADMIN")
    print("💡 Cette désignation devrait déclencher une notification automatique !")
    
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
        
        # Vérifier si la notification a été envoyée
        designation.refresh_from_db()
        if hasattr(designation, 'notification_envoyee'):
            print(f"     📱 Notification envoyée: {designation.notification_envoyee}")
        else:
            print(f"     📱 Pas de champ notification_envoyee")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de la désignation: {e}")
        return False
    
    # 4. Attendre et vérifier
    print("\n⏳ ATTENTE DE LA NOTIFICATION...")
    print("🔔 Vérifiez votre navigateur pour voir la notification push !")
    print("📱 La notification devrait apparaître automatiquement.")
    
    # 5. Vérifier l'état final
    print("\n🔍 VÉRIFICATION FINALE")
    
    designation.refresh_from_db()
    
    print(f"📊 Désignation ID: {designation.id}")
    print(f"👨‍⚖️  Arbitre: {designation.arbitre.get_full_name()}")
    print(f"🏆 Match: {designation.match}")
    print(f"📊 Statut: {designation.get_status_display()}")
    
    # 6. Garder cette désignation pour test
    print("\n💾 DÉSIGNATION CONSERVÉE POUR TEST")
    print("   Cette désignation reste dans la base pour test")
    print("   Vous pouvez la supprimer manuellement plus tard")
    
    print("\n🎯 TEST TERMINÉ!")
    print("💡 Si vous avez reçu une notification, les notifications automatiques fonctionnent !")
    print("   Maintenant, quand vous créerez des désignations via l'admin ou l'API,")
    print("   les arbitres recevront automatiquement des notifications push !")
    
    return True

if __name__ == "__main__":
    success = test_admin_designation()
    sys.exit(0 if success else 1)
