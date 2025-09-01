#!/usr/bin/env python3
"""
Script pour importer les grades d'arbitrage depuis le fichier YAML
"""

import os
import sys
import yaml
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import Grade

def import_grades():
    """Importer les grades depuis le fichier YAML"""
    
    print("🚀 IMPORT DES GRADES D'ARBITRAGE")
    print("=" * 50)
    
    try:
        # Lire le fichier YAML
        yaml_file = os.path.join(os.path.dirname(__file__), 'data', 'grades.yaml')
        
        if not os.path.exists(yaml_file):
            print(f"❌ Fichier YAML non trouvé: {yaml_file}")
            return False
        
        with open(yaml_file, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        if not data or 'grades' not in data:
            print("❌ Structure YAML invalide")
            return False
        
        grades_data = data['grades']
        created_count = 0
        updated_count = 0
        
        for grade_data in grades_data:
            code = grade_data.get('code')
            if not code:
                print(f"⚠️ Grade sans code ignoré: {grade_data}")
                continue
            
            # Vérifier si le grade existe déjà
            grade, created = Grade.objects.get_or_create(
                code=code,
                defaults={
                    'nom': grade_data.get('nom', ''),
                    'description': grade_data.get('description', ''),
                    'niveau': grade_data.get('niveau', 1),
                    'ordre': grade_data.get('ordre', 1),
                    'is_active': grade_data.get('is_active', True)
                }
            )
            
            if created:
                print(f"✅ Grade créé: {grade.nom}")
                created_count += 1
            else:
                # Mettre à jour le grade existant
                grade.nom = grade_data.get('nom', grade.nom)
                grade.description = grade_data.get('description', grade.description)
                grade.niveau = grade_data.get('niveau', grade.niveau)
                grade.ordre = grade_data.get('ordre', grade.ordre)
                grade.is_active = grade_data.get('is_active', grade.is_active)
                grade.save()
                print(f"🔄 Grade mis à jour: {grade.nom}")
                updated_count += 1
        
        print(f"\n🎉 Import terminé!")
        print(f"✅ Grades créés: {created_count}")
        print(f"🔄 Grades mis à jour: {updated_count}")
        print(f"📊 Total des grades: {Grade.objects.count()}")
        
        # Afficher tous les grades
        print(f"\n📋 Grades disponibles:")
        for grade in Grade.objects.all().order_by('ordre'):
            print(f"  {grade.ordre}. {grade.nom} ({grade.code}) - Niveau {grade.niveau}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'import: {e}")
        return False

if __name__ == "__main__":
    success = import_grades()
    sys.exit(0 if success else 1)

