#!/usr/bin/env python3
"""
Script pour nettoyer les types de match dupliqués
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from matches.models import TypeMatch

def cleanup_duplicates():
    """Nettoyer les types de match dupliqués"""
    print("🧹 Nettoyage des types de match dupliqués...")
    print("=" * 50)
    
    # Types à conserver (les originaux avec codes courts)
    keep_codes = ['L1', 'L2', 'C1', 'C2', 'JUN', 'CT']
    
    # Types à supprimer (les nouveaux avec codes longs)
    remove_codes = ['ligue1', 'ligue2', 'c1', 'c2', 'jeunes', 'coupe_tunisie']
    
    print("📋 Types à conserver (codes courts):")
    for code in keep_codes:
        try:
            match_type = TypeMatch.objects.get(code=code)
            print(f"   ✅ {match_type.nom} (code: {match_type.code})")
        except TypeMatch.DoesNotExist:
            print(f"   ❌ Code {code} non trouvé")
    
    print("\n📋 Types à supprimer (codes longs):")
    deleted_count = 0
    for code in remove_codes:
        try:
            match_type = TypeMatch.objects.get(code=code)
            print(f"   🗑️ Suppression: {match_type.nom} (code: {match_type.code})")
            match_type.delete()
            deleted_count += 1
        except TypeMatch.DoesNotExist:
            print(f"   ⚠️ Code {code} déjà supprimé")
    
    print(f"\n📊 Résultat: {deleted_count} type(s) supprimé(s)")
    
    # Vérifier le résultat final
    print("\n🔍 Vérification finale:")
    remaining_types = TypeMatch.objects.all().order_by('created_at')
    print(f"📊 Total restant: {remaining_types.count()}")
    
    for match_type in remaining_types:
        print(f"   - {match_type.nom} (code: {match_type.code})")

if __name__ == '__main__':
    cleanup_duplicates()





