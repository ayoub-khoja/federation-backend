#!/usr/bin/env python
"""
Test manuel d'envoi de notification
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from matches.models import Designation
from firebase_config import send_notification_to_user

def test_notification():
    """Test d'envoi de notification manuel"""
    print("🧪 Test d'envoi de notification manuel")
    print("=" * 50)
    
    # Récupérer la dernière désignation
    d = Designation.objects.filter(arbitre_id=28).last()
    if not d:
        print("❌ Aucune désignation trouvée")
        return
    
    print(f"📋 Désignation trouvée:")
    print(f"   - Arbitre: {d.arbitre.get_full_name()}")
    print(f"   - Match: {d.match.home_team} vs {d.match.away_team}")
    print(f"   - Statut: {d.status}")
    
    # Tester l'envoi de notification
    print("\n📤 Envoi de notification...")
    try:
        result = send_notification_to_user(
            user=d.arbitre,
            title="🏆 Nouvelle Désignation",
            body=f"Vous avez été désigné pour {d.match.home_team} vs {d.match.away_team}",
            data={
                'type': 'designation',
                'match_id': d.match.id,
                'designation_type': 'arbitre_principal'
            }
        )
        
        print(f"✅ Résultat: {result}")
        
        if result.get('errors', 0) == 0:
            print("🎉 Notification envoyée avec succès!")
        else:
            print(f"⚠️ {result.get('errors', 0)} erreur(s) lors de l'envoi")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_notification()


















