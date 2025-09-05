#!/usr/bin/env python3
"""
Script pour mettre à jour automatiquement les statuts des matchs selon leur date
"""
import os
import django
from datetime import date, datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from matches.models import Match

def update_match_status():
    """Mettre à jour automatiquement les statuts des matchs"""
    print("🔄 Mise à jour automatique des statuts des matchs...")
    print("=" * 60)
    
    today = date.today()
    print(f"📅 Date d'aujourd'hui: {today}")
    
    # Récupérer tous les matchs
    all_matches = Match.objects.all()
    print(f"📊 Total des matchs: {all_matches.count()}")
    
    if all_matches.count() == 0:
        print("❌ Aucun match trouvé")
        return
    
    # Statistiques avant mise à jour
    print("\n📋 Statuts avant mise à jour:")
    status_before = {}
    for match in all_matches:
        status = match.status
        status_before[status] = status_before.get(status, 0) + 1
    
    for status, count in status_before.items():
        print(f"   {status}: {count} match(s)")
    
    # Mettre à jour les statuts
    updated_count = 0
    for match in all_matches:
        old_status = match.status
        new_status = None
        
        if match.match_date < today:
            # Match passé → terminé
            new_status = 'completed'
        elif match.match_date == today:
            # Match d'aujourd'hui → en cours
            new_status = 'in_progress'
        else:
            # Match futur → programmé
            new_status = 'scheduled'
        
        # Mettre à jour seulement si le statut change
        if old_status != new_status:
            match.status = new_status
            match.save()
            updated_count += 1
            print(f"   ✅ {match.home_team} vs {match.away_team} ({match.match_date}): {old_status} → {new_status}")
    
    print(f"\n📊 Résultat: {updated_count} match(s) mis à jour")
    
    # Statistiques après mise à jour
    print("\n📋 Statuts après mise à jour:")
    status_after = {}
    for match in Match.objects.all():
        status = match.status
        status_after[status] = status_after.get(status, 0) + 1
    
    for status, count in status_after.items():
        print(f"   {status}: {count} match(s)")

if __name__ == '__main__':
    update_match_status()





