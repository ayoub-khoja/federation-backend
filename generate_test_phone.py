#!/usr/bin/env python
"""
Script pour générer des numéros de téléphone uniques pour les tests
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import Arbitre

def generate_unique_phone():
    """Génère un numéro de téléphone unique pour les tests"""
    base_number = 12345678  # Numéro de base
    
    for i in range(100):  # Essayer jusqu'à 100 numéros
        test_number = f"+216{base_number + i}"
        
        # Vérifier si le numéro existe déjà
        if not Arbitre.objects.filter(phone_number=test_number).exists():
            print(f"✅ Numéro de téléphone unique disponible: {test_number}")
            return test_number
    
    print("❌ Aucun numéro de téléphone unique trouvé dans la plage testée")
    return None

def list_existing_phones():
    """Liste les numéros de téléphone existants"""
    print("📱 Numéros de téléphone existants:")
    arbitres = Arbitre.objects.all().values_list('phone_number', 'first_name', 'last_name')
    
    if not arbitres:
        print("   Aucun arbitre enregistré")
    else:
        for phone, first_name, last_name in arbitres:
            print(f"   {phone} - {first_name} {last_name}")

if __name__ == "__main__":
    print("🔍 Vérification des numéros de téléphone existants...")
    list_existing_phones()
    print()
    
    print("🔧 Génération d'un numéro de téléphone unique pour les tests...")
    unique_phone = generate_unique_phone()
    
    if unique_phone:
        print(f"\n💡 Utilisez ce numéro pour vos tests: {unique_phone}")
        print("   Exemple de données de test:")
        print(f'   {{"phone_number": "{unique_phone}", "first_name": "Test", "last_name": "User", ...}}')
    else:
        print("\n❌ Impossible de générer un numéro unique. Supprimez des comptes de test ou utilisez un autre format.")
