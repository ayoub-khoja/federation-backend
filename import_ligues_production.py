#!/usr/bin/env python3
"""
Script pour importer les ligues d'arbitrage en production
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
from accounts.models import LigueArbitrage

def import_ligues_from_yaml(yaml_file_path=None):
    """
    Importe les ligues depuis le fichier YAML vers la base de données de production
    """
    if yaml_file_path is None:
        yaml_file_path = backend_dir / 'data' / 'ligues.yaml'
    
    print(f"🚀 Importation des ligues depuis: {yaml_file_path}")
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
        
        if 'ligues_tunisiennes' not in data:
            print("❌ Erreur: Le fichier YAML doit contenir une clé 'ligues_tunisiennes'")
            return False
        
        ligues_data = data['ligues_tunisiennes']
        print(f"📊 Trouvé {len(ligues_data)} ligues dans le fichier YAML")
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for ligue_info in ligues_data:
            # Vérifier les champs requis
            if 'nom' not in ligue_info:
                print(f"⚠️  Ligue ignorée - champ 'nom' manquant: {ligue_info}")
                skipped_count += 1
                continue
            
            # Créer ou mettre à jour la ligue
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
                print(f"✅ Ligue créée: {ligue.nom} (Région: {ligue.description})")
            else:
                # Mettre à jour la ligue existante
                ligue.description = ligue_info.get('region', ligue.description)
                ligue.is_active = ligue_info.get('active', True)
                ligue.ordre = ligue_info.get('ordre', ligue.ordre)
                ligue.save()
                updated_count += 1
                print(f"🔄 Ligue mise à jour: {ligue.nom} (Région: {ligue.description})")
        
        # Résumé
        print("\n" + "=" * 50)
        print("📈 RÉSUMÉ DE L'IMPORTATION")
        print("=" * 50)
        print(f"✅ Ligues créées: {created_count}")
        print(f"🔄 Ligues mises à jour: {updated_count}")
        print(f"⚠️  Ligues ignorées: {skipped_count}")
        print(f"📊 Total en base: {LigueArbitrage.objects.count()}")
        
        # Afficher toutes les ligues actives
        print("\n" + "=" * 50)
        print("🏆 LIGUES ACTIVES EN BASE")
        print("=" * 50)
        for ligue in LigueArbitrage.objects.filter(is_active=True).order_by('ordre', 'nom'):
            print(f"• {ligue.nom} - {ligue.description} (Ordre: {ligue.ordre})")
        
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
    print("🏛️  IMPORTATION DES LIGUES D'ARBITRAGE - PRODUCTION")
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
    success = import_ligues_from_yaml()
    
    if success:
        print("\n✅ Importation réussie!")
        sys.exit(0)
    else:
        print("\n❌ Importation échouée!")
        sys.exit(1)

if __name__ == "__main__":
    main()
