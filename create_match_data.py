#!/usr/bin/env python
"""
Script pour créer les données initiales des types de match et catégories
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from matches.models import TypeMatch, Categorie

def create_match_types():
    """Créer les types de match"""
    types_data = [
        {
            'nom': 'Ligue 1',
            'code': 'L1',
            'description': 'Championnat de Ligue 1 Professionnelle',
            'ordre': 1
        },
        {
            'nom': 'Ligue 2',
            'code': 'L2',
            'description': 'Championnat de Ligue 2 Professionnelle',
            'ordre': 2
        },
        {
            'nom': 'C1',
            'code': 'C1',
            'description': 'Coupe de Tunisie',
            'ordre': 3
        },
        {
            'nom': 'C2',
            'code': 'C2',
            'description': 'Coupe de la Ligue',
            'ordre': 4
        },
        {
            'nom': 'Jeunes',
            'code': 'JUN',
            'description': 'Championnat des Jeunes',
            'ordre': 5
        },
        {
            'nom': 'Coupe de Tunisie',
            'code': 'CT',
            'description': 'Coupe de Tunisie',
            'ordre': 6
        }
    ]
    
    for type_data in types_data:
        type_match, created = TypeMatch.objects.get_or_create(
            code=type_data['code'],
            defaults=type_data
        )
        if created:
            print(f"✓ Type de match créé: {type_match.nom}")
        else:
            print(f"- Type de match existe déjà: {type_match.nom}")

def create_categories():
    """Créer les catégories"""
    categories_data = [
        {
            'nom': 'U21',
            'code': 'U21',
            'age_min': 18,
            'age_max': 21,
            'description': 'Catégorie moins de 21 ans',
            'ordre': 1
        },
        {
            'nom': 'U19',
            'code': 'U19',
            'age_min': 16,
            'age_max': 19,
            'description': 'Catégorie moins de 19 ans',
            'ordre': 2
        },
        {
            'nom': 'U17',
            'code': 'U17',
            'age_min': 15,
            'age_max': 17,
            'description': 'Catégorie moins de 17 ans',
            'ordre': 3
        },
        {
            'nom': 'U16',
            'code': 'U16',
            'age_min': 14,
            'age_max': 16,
            'description': 'Catégorie moins de 16 ans',
            'ordre': 4
        },
        {
            'nom': 'U15',
            'code': 'U15',
            'age_min': 13,
            'age_max': 15,
            'description': 'Catégorie moins de 15 ans',
            'ordre': 5
        }
    ]
    
    for category_data in categories_data:
        categorie, created = Categorie.objects.get_or_create(
            code=category_data['code'],
            defaults=category_data
        )
        if created:
            print(f"✓ Catégorie créée: {categorie.nom}")
        else:
            print(f"- Catégorie existe déjà: {categorie.nom}")

def main():
    """Fonction principale"""
    print("=== Création des données initiales ===")
    print()
    
    print("1. Création des types de match...")
    create_match_types()
    print()
    
    print("2. Création des catégories...")
    create_categories()
    print()
    
    print("=== Données créées avec succès ! ===")
    print()
    print("Types de match disponibles:")
    for type_match in TypeMatch.objects.all():
        print(f"  - {type_match.nom} ({type_match.code})")
    
    print()
    print("Catégories disponibles:")
    for categorie in Categorie.objects.all():
        print(f"  - {categorie.nom} ({categorie.code})")

if __name__ == '__main__':
    main()
