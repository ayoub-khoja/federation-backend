#!/usr/bin/env python
"""
Script pour importer les ligues depuis le fichier YAML
"""
import os
import yaml
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import LigueArbitrage

def import_ligues():
    """Importer les ligues depuis le fichier YAML"""
    
    print("🏆 IMPORT DES LIGUES DEPUIS LE FICHIER YAML")
    print("=" * 60)
    
    # Lire le fichier YAML
    yaml_file = 'data/ligues.yaml'
    
    try:
        with open(yaml_file, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"❌ Fichier {yaml_file} non trouvé")
        return
    except yaml.YAMLError as e:
        print(f"❌ Erreur de parsing YAML: {e}")
        return
    
    # Extraire les ligues
    ligues_data = data.get('ligues_tunisiennes', [])
    
    if not ligues_data:
        print("❌ Aucune ligue trouvée dans le fichier YAML")
        return
    
    print(f"📋 {len(ligues_data)} ligues trouvées dans le fichier YAML")
    print()
    
    # Importer chaque ligue
    created_count = 0
    updated_count = 0
    
    for ligue_data in ligues_data:
        code = ligue_data.get('code')
        nom = ligue_data.get('nom')
        region = ligue_data.get('region')
        active = ligue_data.get('active', True)
        ordre = ligue_data.get('ordre', 0)
        
        print(f"🏁 Traitement: {nom} ({region})")
        
        # Vérifier si la ligue existe déjà
        ligue, created = LigueArbitrage.objects.get_or_create(
            code=code,
            defaults={
                'nom': nom,
                'region': region,
                'is_active': active,
                'ordre': ordre,
                'description': f"Ligue d'arbitrage de {region}"
            }
        )
        
        if created:
            print(f"   ✅ Créée: {nom}")
            created_count += 1
        else:
            # Mettre à jour les informations
            ligue.nom = nom
            ligue.region = region
            ligue.is_active = active
            ligue.ordre = ordre
            ligue.description = f"Ligue d'arbitrage de {region}"
            ligue.save()
            print(f"   🔄 Mise à jour: {nom}")
            updated_count += 1
    
    print()
    print("📊 RÉSUMÉ DE L'IMPORT")
    print("=" * 60)
    print(f"   🆕 Ligues créées: {created_count}")
    print(f"   🔄 Ligues mises à jour: {updated_count}")
    print(f"   📋 Total traitées: {created_count + updated_count}")
    
    # Afficher toutes les ligues dans la base
    print()
    print("🏆 LIGUES DANS LA BASE DE DONNÉES")
    print("=" * 60)
    
    all_ligues = LigueArbitrage.objects.all().order_by('ordre')
    for ligue in all_ligues:
        status = "✅ Actif" if ligue.is_active else "❌ Inactif"
        print(f"   {ligue.ordre:2d}. {ligue.nom} ({ligue.region}) - {status}")

if __name__ == "__main__":
    import_ligues()
