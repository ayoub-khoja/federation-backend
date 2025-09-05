#!/usr/bin/env python3
"""
Script pour vérifier et nettoyer les types de match dupliqués
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from matches.models import TypeMatch

def check_duplicates():
    """Vérifier les types de match dupliqués"""
    print("🔍 Vérification des types de match...")
    print("=" * 50)
    
    all_types = TypeMatch.objects.all().order_by('created_at')
    
    print(f"📊 Total des types de match: {all_types.count()}")
    print("\n📋 Liste complète:")
    
    for i, match_type in enumerate(all_types, 1):
        print(f"{i:2d}. {match_type.nom} (code: {match_type.code}) - Créé: {match_type.created_at.strftime('%d/%m/%Y %H:%M')}")
    
    # Identifier les doublons par nom
    print("\n🔍 Recherche de doublons par nom:")
    names = {}
    for match_type in all_types:
        if match_type.nom in names:
            names[match_type.nom].append(match_type)
        else:
            names[match_type.nom] = [match_type]
    
    duplicates = {name: types for name, types in names.items() if len(types) > 1}
    
    if duplicates:
        print("⚠️ Doublons trouvés:")
        for name, types in duplicates.items():
            print(f"\n   {name}:")
            for match_type in types:
                print(f"     - Code: {match_type.code}, Créé: {match_type.created_at.strftime('%d/%m/%Y %H:%M')}")
    else:
        print("✅ Aucun doublon trouvé")

if __name__ == '__main__':
    check_duplicates()





