#!/usr/bin/env python3
"""
Script pour importer les grades d'arbitrage en production
Utilise la configuration de production Django
"""

import os
import sys
import django
import yaml
from pathlib import Path

# Ajouter le répertoire backend au path Python
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configuration de l'environnement Django pour la production
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings_production')

# Initialiser Django
django.setup()

# Maintenant on peut importer les modèles Django
from accounts.models import GradeArbitrage

def import_grades_from_yaml(yaml_file_path=None):
    """
    Importe les grades depuis le fichier YAML vers la base de données de production
    """
    if yaml_file_path is None:
        yaml_file_path = backend_dir / 'data' / 'grades.yaml'
    
    print(f"🚀 Importation des grades depuis: {yaml_file_path}")
    print(f"🌍 Mode: PRODUCTION")
    print(f"🗄️ Base de données: PostgreSQL")
    print("=" * 50)
    
    # Vérifier que le fichier existe
    if not os.path.exists(yaml_file_path):
        print(f"❌ Erreur: Le fichier {yaml_file_path} n'existe pas")
        return False
    
    try:
        # Lire le fichier YAML
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        if 'grades' not in data:
            print("❌ Erreur: Le fichier YAML doit contenir une clé 'grades'")
            return False
        
        grades_data = data['grades']
        print(f"📊 Trouvé {len(grades_data)} grades dans le fichier YAML")
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for grade_info in grades_data:
            # Vérifier les champs requis
            if 'nom' not in grade_info or 'code' not in grade_info:
                print(f"⚠️  Grade ignoré - champs 'nom' ou 'code' manquants: {grade_info}")
                skipped_count += 1
                continue
            
            # Créer ou mettre à jour le grade
            grade, created = GradeArbitrage.objects.get_or_create(
                code=grade_info['code'],
                defaults={
                    'nom': grade_info['nom'],
                    'description': grade_info.get('description', ''),
                    'niveau': grade_info.get('niveau', 1),
                    'ordre': grade_info.get('ordre', 0),
                    'is_active': grade_info.get('is_active', True),
                }
            )
            
            if created:
                created_count += 1
                print(f"✅ Grade créé: {grade.nom} (Code: {grade.code}, Niveau: {grade.niveau})")
            else:
                # Mettre à jour le grade existant
                grade.nom = grade_info['nom']
                grade.description = grade_info.get('description', grade.description)
                grade.niveau = grade_info.get('niveau', grade.niveau)
                grade.ordre = grade_info.get('ordre', grade.ordre)
                grade.is_active = grade_info.get('is_active', grade.is_active)
                grade.save()
                updated_count += 1
                print(f"🔄 Grade mis à jour: {grade.nom} (Code: {grade.code}, Niveau: {grade.niveau})")
        
        # Résumé
        print("\n" + "=" * 50)
        print("📈 RÉSUMÉ DE L'IMPORTATION")
        print("=" * 50)
        print(f"✅ Grades créés: {created_count}")
        print(f"🔄 Grades mis à jour: {updated_count}")
        print(f"⚠️  Grades ignorés: {skipped_count}")
        print(f"📊 Total en base: {GradeArbitrage.objects.count()}")
        
        # Afficher tous les grades actifs
        print("\n" + "=" * 50)
        print("🏆 GRADES ACTIFS EN BASE")
        print("=" * 50)
        for grade in GradeArbitrage.objects.filter(is_active=True).order_by('ordre', 'niveau', 'nom'):
            print(f"• {grade.nom} - Niveau {grade.niveau} (Code: {grade.code})")
        
        print("\n🎉 Importation terminée avec succès!")
        return True
        
    except yaml.YAMLError as e:
        print(f"❌ Erreur lors de la lecture du fichier YAML: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def main():
    """Fonction principale"""
    print("🏆 IMPORTATION DES GRADES D'ARBITRAGE - PRODUCTION")
    print("=" * 60)
    
    # Vérifier la configuration de production
    from django.conf import settings
    print(f"🔧 Configuration: {settings.SETTINGS_MODULE}")
    print(f"🗄️ Base de données: {settings.DATABASES['default']['ENGINE']}")
    print(f"🌍 DEBUG: {settings.DEBUG}")
    
    # Demander confirmation
    response = input("\n❓ Voulez-vous continuer avec l'importation? (oui/non): ")
    if response.lower() not in ['oui', 'o', 'yes', 'y']:
        print("❌ Importation annulée par l'utilisateur")
        return
    
    # Lancer l'importation
    success = import_grades_from_yaml()
    
    if success:
        print("\n✅ Importation réussie!")
        sys.exit(0)
    else:
        print("\n❌ Importation échouée!")
        sys.exit(1)

if __name__ == "__main__":
    main()
