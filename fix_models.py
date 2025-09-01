#!/usr/bin/env python3
"""
Script pour corriger les choix de grades dans les modèles Arbitre et Commissaire
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import Arbitre, Commissaire

def fix_grades():
    """Corriger les grades existants dans la base de données"""
    
    # Mapping des anciens grades vers les nouveaux
    grade_mapping = {
        'debutant': 'candidat',
        'regional': '3eme_serie',
        'national': '2eme_serie',
        'international': '1ere_serie'
    }
    
    print("Correction des grades des arbitres...")
    arbitres_updated = 0
    for arbitre in Arbitre.objects.all():
        if arbitre.grade in grade_mapping:
            old_grade = arbitre.grade
            arbitre.grade = grade_mapping[old_grade]
            arbitre.save()
            arbitres_updated += 1
            print(f"  Arbitre {arbitre.get_full_name()}: {old_grade} -> {arbitre.grade}")
    
    print(f"\nCorrection des grades des commissaires...")
    commissaires_updated = 0
    for commissaire in Commissaire.objects.all():
        if commissaire.grade in grade_mapping:
            old_grade = commissaire.grade
            commissaire.grade = grade_mapping[old_grade]
            commissaire.save()
            commissaires_updated += 1
            print(f"  Commissaire {commissaire.get_full_name()}: {old_grade} -> {commissaire.grade}")
    
    print(f"\nRésumé:")
    print(f"  Arbitres mis à jour: {arbitres_updated}")
    print(f"  Commissaires mis à jour: {commissaires_updated}")
    print(f"  Total: {arbitres_updated + commissaires_updated}")

if __name__ == '__main__':
    try:
        fix_grades()
        print("\n✅ Correction des grades terminée avec succès!")
    except Exception as e:
        print(f"\n❌ Erreur lors de la correction: {e}")
