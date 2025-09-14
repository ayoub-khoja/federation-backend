#!/usr/bin/env python3
"""
Script pour importer toutes les données de référence en production
- Ligues d'arbitrage
- Grades d'arbitrage
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
from accounts.models import LigueArbitrage, GradeArbitrage

def import_ligues_from_yaml(yaml_file_path=None):
    """Importe les ligues depuis le fichier YAML"""
    if yaml_file_path is None:
        yaml_file_path = backend_dir / 'data' / 'ligues.yaml'
    
    print(f"🏛️  Importation des ligues depuis: {yaml_file_path}")
    
    if not os.path.exists(yaml_file_path):
        print(f"❌ Erreur: Le fichier {yaml_file_path} n'existe pas")
        return False
    
    try:
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        if 'ligues_tunisiennes' not in data:
            print("❌ Erreur: Le fichier YAML doit contenir une clé 'ligues_tunisiennes'")
            return False
        
        ligues_data = data['ligues_tunisiennes']
        print(f"📊 Trouvé {len(ligues_data)} ligues dans le fichier YAML")
        
        created_count = 0
        updated_count = 0
        
        for ligue_info in ligues_data:
            if 'nom' not in ligue_info:
                print(f"⚠️  Ligue ignorée - champ 'nom' manquant: {ligue_info}")
                continue
            
            ligue, created = LigueArbitrage.objects.get_or_create(
                nom=ligue_info['nom'],
                defaults={
                    'description': ligue_info.get('region', ''),
                    'is_active': ligue_info.get('active', True),
                    'ordre': ligue_info.get('ordre', 0),
                }
            )
            
            if created:
                created_count += 1
                print(f"✅ Ligue créée: {ligue.nom}")
            else:
                ligue.description = ligue_info.get('region', ligue.description)
                ligue.is_active = ligue_info.get('active', True)
                ligue.ordre = ligue_info.get('ordre', ligue.ordre)
                ligue.save()
                updated_count += 1
                print(f"🔄 Ligue mise à jour: {ligue.nom}")
        
        print(f"📈 Ligues - Créées: {created_count}, Mises à jour: {updated_count}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'importation des ligues: {e}")
        return False

def import_grades_from_yaml(yaml_file_path=None):
    """Importe les grades depuis le fichier YAML"""
    if yaml_file_path is None:
        yaml_file_path = backend_dir / 'data' / 'grades.yaml'
    
    print(f"🏆 Importation des grades depuis: {yaml_file_path}")
    
    if not os.path.exists(yaml_file_path):
        print(f"❌ Erreur: Le fichier {yaml_file_path} n'existe pas")
        return False
    
    try:
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
        
        if 'grades' not in data:
            print("❌ Erreur: Le fichier YAML doit contenir une clé 'grades'")
            return False
        
        grades_data = data['grades']
        print(f"📊 Trouvé {len(grades_data)} grades dans le fichier YAML")
        
        created_count = 0
        updated_count = 0
        
        for grade_info in grades_data:
            if 'nom' not in grade_info or 'code' not in grade_info:
                print(f"⚠️  Grade ignoré - champs 'nom' ou 'code' manquants: {grade_info}")
                continue
            
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
                print(f"✅ Grade créé: {grade.nom}")
            else:
                grade.nom = grade_info['nom']
                grade.description = grade_info.get('description', grade.description)
                grade.niveau = grade_info.get('niveau', grade.niveau)
                grade.ordre = grade_info.get('ordre', grade.ordre)
                grade.is_active = grade_info.get('is_active', grade.is_active)
                grade.save()
                updated_count += 1
                print(f"🔄 Grade mis à jour: {grade.nom}")
        
        print(f"📈 Grades - Créés: {created_count}, Mis à jour: {updated_count}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'importation des grades: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 IMPORTATION COMPLÈTE DES DONNÉES DE RÉFÉRENCE - PRODUCTION")
    print("=" * 70)
    
    # Vérifier la configuration de production
    from django.conf import settings
    print(f"🔧 Configuration: {settings.SETTINGS_MODULE}")
    print(f"🗄️ Base de données: {settings.DATABASES['default']['ENGINE']}")
    print(f"🌍 DEBUG: {settings.DEBUG}")
    print("")
    
    # Demander confirmation
    response = input("❓ Voulez-vous continuer avec l'importation complète? (oui/non): ")
    if response.lower() not in ['oui', 'o', 'yes', 'y']:
        print("❌ Importation annulée par l'utilisateur")
        return
    
    print("\n" + "=" * 70)
    print("🚀 DÉBUT DE L'IMPORTATION")
    print("=" * 70)
    
    # Importation des ligues
    print("\n1️⃣ IMPORTATION DES LIGUES")
    print("-" * 30)
    ligues_success = import_ligues_from_yaml()
    
    # Importation des grades
    print("\n2️⃣ IMPORTATION DES GRADES")
    print("-" * 30)
    grades_success = import_grades_from_yaml()
    
    # Résumé final
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ FINAL")
    print("=" * 70)
    
    if ligues_success:
        print(f"✅ Ligues: {LigueArbitrage.objects.count()} en base")
    else:
        print("❌ Ligues: Erreur lors de l'importation")
    
    if grades_success:
        print(f"✅ Grades: {GradeArbitrage.objects.count()} en base")
    else:
        print("❌ Grades: Erreur lors de l'importation")
    
    # Afficher les données actives
    if ligues_success:
        print("\n🏛️  LIGUES ACTIVES:")
        for ligue in LigueArbitrage.objects.filter(is_active=True).order_by('ordre', 'nom'):
            print(f"   • {ligue.nom} - {ligue.description}")
    
    if grades_success:
        print("\n🏆 GRADES ACTIFS:")
        for grade in GradeArbitrage.objects.filter(is_active=True).order_by('ordre', 'niveau', 'nom'):
            print(f"   • {grade.nom} - Niveau {grade.niveau}")
    
    if ligues_success and grades_success:
        print("\n🎉 Importation complète réussie!")
        sys.exit(0)
    else:
        print("\n❌ Importation partiellement échouée!")
        sys.exit(1)

if __name__ == "__main__":
    main()
