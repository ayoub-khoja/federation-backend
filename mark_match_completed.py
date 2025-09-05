#!/usr/bin/env python3
"""
Script pour marquer un match comme terminé
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from matches.models import Match

def mark_match_completed():
    """Marquer un match comme terminé"""
    print("🏁 Marquage d'un match comme terminé...")
    print("=" * 50)
    
    # Récupérer le premier match programmé
    match = Match.objects.filter(status='scheduled').first()
    
    if not match:
        print("❌ Aucun match programmé trouvé")
        return
    
    print(f"📋 Match trouvé: {match.home_team} vs {match.away_team}")
    print(f"   Date: {match.match_date}")
    print(f"   Type: {match.type_match.nom if match.type_match else 'Non défini'}")
    print(f"   Statut actuel: {match.status}")
    
    # Marquer comme terminé avec un score
    match.status = 'completed'
    match.home_score = 2
    match.away_score = 1
    match.match_report = "Match terminé avec succès"
    match.save()
    
    print(f"\n✅ Match marqué comme terminé")
    print(f"   Score: {match.home_team} {match.home_score} - {match.away_score} {match.away_team}")
    print(f"   Nouveau statut: {match.status}")
    
    # Vérifier le résultat
    completed_matches = Match.objects.filter(status='completed').count()
    print(f"\n📊 Total des matchs terminés: {completed_matches}")

if __name__ == '__main__':
    mark_match_completed()





