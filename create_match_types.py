#!/usr/bin/env python3
"""
Script pour créer les types de match dans la base de données
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from matches.models import TypeMatch

def create_match_types():
    """Créer les types de match"""
    match_types = [
        {
            'code': 'ligue1',
            'nom': 'Ligue 1',
            'description': 'Championnat de Ligue 1 Tunisienne',
            'is_active': True
        },
        {
            'code': 'ligue2',
            'nom': 'Ligue 2',
            'description': 'Championnat de Ligue 2 Tunisienne',
            'is_active': True
        },
        {
            'code': 'c1',
            'nom': 'Ligue des Champions',
            'description': 'Ligue des Champions Africaine',
            'is_active': True
        },
        {
            'code': 'c2',
            'nom': 'Ligue des Champions 2',
            'description': 'Ligue des Champions 2 Africaine',
            'is_active': True
        },
        {
            'code': 'jeunes',
            'nom': 'Championnat Jeunes',
            'description': 'Championnat des jeunes',
            'is_active': True
        },
        {
            'code': 'coupe_tunisie',
            'nom': 'Coupe de Tunisie',
            'description': 'Coupe de Tunisie de Football',
            'is_active': True
        }
    ]
    
    created_count = 0
    for match_type_data in match_types:
        match_type, created = TypeMatch.objects.get_or_create(
            code=match_type_data['code'],
            defaults=match_type_data
        )
        if created:
            print(f"✅ Créé: {match_type.nom}")
            created_count += 1
        else:
            print(f"⚠️ Existe déjà: {match_type.nom}")
    
    print(f"\n📊 Résultat: {created_count} type(s) créé(s) sur {len(match_types)}")

if __name__ == '__main__':
    create_match_types()
