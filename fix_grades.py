#!/usr/bin/env python3
"""
Script pour corriger les grades d'arbitrage dans la base de données
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import Arbitre, Commissaire

def fix_grades():
    """Corriger les grades dans la base de données"""
    
    print("🔧 CORRECTION DES GRADES D'ARBITRAGE")
    print("=" * 50)
    
    # Mapping des anciens grades vers les nouveaux
    grade_mapping = {
        'debutant': 'candidat',
        'regional': '3eme_serie',
        'national': '2eme_serie',
        'international': '1ere_serie'
    }
    
    # Corriger les arbitres
    arbitres_updated = 0
    for arbitre in Arbitre.objects.all():
        old_grade = arbitre.grade
        if old_grade in grade_mapping:
            arbitre.grade = grade_mapping[old_grade]
            arbitre.save()
            print(f"✅ Arbitre {arbitre.get_full_name()}: {old_grade} → {arbitre.grade}")
            arbitres_updated += 1
    
    # Corriger les commissaires
    commissaires_updated = 0
    for commissaire in Commissaire.objects.all():
        old_grade = commissaire.grade
        if old_grade in grade_mapping:
            commissaire.grade = grade_mapping[old_grade]
            commissaire.save()
            print(f"✅ Commissaire {commissaire.get_full_name()}: {old_grade} → {commissaire.grade}")
            commissaires_updated += 1
    
    print(f"\n🎉 Correction terminée!")
    print(f"✅ Arbitres mis à jour: {arbitres_updated}")
    print(f"✅ Commissaires mis à jour: {commissaires_updated}")
    
    return True

if __name__ == "__main__":
    success = fix_grades()
    
    if success:
        print("\n✅ Correction réussie!")
        sys.exit(0)
    else:
        print("\n❌ Correction échouée!")
        sys.exit(1)






























