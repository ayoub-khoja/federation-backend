#!/usr/bin/env python3
"""
Script pour vérifier les statuts des matchs dans la base de données
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from matches.models import Match, TypeMatch

def check_match_status():
    """Vérifier les statuts des matchs"""
    print("🔍 Vérification des matchs dans la base de données...")
    print("=" * 60)
    
    # Compter tous les matchs
    total_matches = Match.objects.count()
    print(f"📊 Total des matchs: {total_matches}")
    
    if total_matches == 0:
        print("❌ Aucun match trouvé dans la base de données")
        return
    
    # Vérifier les statuts
    print("\n📋 Répartition par statut:")
    status_counts = {}
    for match in Match.objects.all():
        status = match.status
        if status in status_counts:
            status_counts[status] += 1
        else:
            status_counts[status] = 1
    
    for status, count in status_counts.items():
        print(f"   {status}: {count} match(s)")
    
    # Afficher quelques exemples de matchs
    print("\n📋 Exemples de matchs:")
    for i, match in enumerate(Match.objects.all()[:5], 1):
        print(f"{i}. {match.home_team} vs {match.away_team}")
        print(f"   Date: {match.match_date}")
        print(f"   Statut: {match.status}")
        print(f"   Type: {match.type_match.nom if match.type_match else 'Non défini'}")
        print(f"   Arbitre: {match.referee.get_full_name() if match.referee else 'Non assigné'}")
        print()
    
    # Vérifier les matchs terminés spécifiquement
    completed_matches = Match.objects.filter(status='completed').count()
    print(f"🏁 Matchs terminés (status='completed'): {completed_matches}")
    
    # Vérifier les matchs par type
    print("\n📊 Matchs par type:")
    for match_type in TypeMatch.objects.all():
        count = Match.objects.filter(type_match=match_type).count()
        completed_count = Match.objects.filter(type_match=match_type, status='completed').count()
        print(f"   {match_type.nom} ({match_type.code}): {count} total, {completed_count} terminés")

if __name__ == '__main__':
    check_match_status()



