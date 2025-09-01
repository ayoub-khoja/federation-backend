#!/usr/bin/env python
"""
Script d'initialisation de la base de données
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import LigueArbitrage, Arbitre, Commissaire, Admin
from django.contrib.auth.hashers import make_password

def create_test_data():
    """Créer des données de test"""
    print("🚀 Initialisation de la base de données")
    print("=" * 50)
    
    # 1. Créer une ligue de test
    ligue, created = LigueArbitrage.objects.get_or_create(
        nom="Ligue de Tunis",
        defaults={
            'region': 'Tunis',
            'description': 'Ligue principale de Tunis',
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ Ligue créée: {ligue.nom} - {ligue.region}")
    else:
        print(f"ℹ️ Ligue existante: {ligue.nom} - {ligue.region}")
    
    # 2. Créer un administrateur de test
    admin, created = Admin.objects.get_or_create(
        phone_number="+21611111111",
        defaults={
            'email': 'admin@dna.tn',
            'first_name': 'Mohamed',
            'last_name': 'Ben Ali',
            'password': make_password('admin123456'),
            'user_type': 'admin',
            'department': 'Direction Générale',
            'position': 'Directeur',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    if created:
        print(f"✅ Administrateur créé: {admin.first_name} {admin.last_name}")
    else:
        print(f"ℹ️ Administrateur existant: {admin.first_name} {admin.last_name}")
    
    # 3. Créer un arbitre de test
    arbitre, created = Arbitre.objects.get_or_create(
        phone_number="+21622222222",
        defaults={
            'email': 'arbitre@dna.tn',
            'first_name': 'Ali',
            'last_name': 'Ben Salah',
            'password': make_password('arbitre123456'),
            'grade': 'national',
            'ligue': ligue,
            'birth_date': '1985-06-15',
            'birth_place': 'Sousse',
            'address': '456 Avenue Habib Bourguiba, Sousse',
            'date_debut': '2010-01-01'
        }
    )
    
    if created:
        print(f"✅ Arbitre créé: {arbitre.first_name} {arbitre.last_name}")
    else:
        print(f"ℹ️ Arbitre existant: {arbitre.first_name} {arbitre.last_name}")
    
    # 4. Créer un commissaire de test
    commissaire, created = Commissaire.objects.get_or_create(
        phone_number="+21633333333",
        defaults={
            'email': 'commissaire@dna.tn',
            'first_name': 'Fatma',
            'last_name': 'Ben Othman',
            'password': make_password('commissaire123456'),
            'specialite': 'commissaire_match',
            'grade': 'regional',
            'ligue': ligue,
            'birth_date': '1988-03-20',
            'birth_place': 'Monastir',
            'address': '789 Rue de la République, Monastir',
            'date_debut': '2012-01-01'
        }
    )
    
    if created:
        print(f"✅ Commissaire créé: {commissaire.first_name} {commissaire.last_name}")
    else:
        print(f"ℹ️ Commissaire existant: {commissaire.first_name} {commissaire.last_name}")
    
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DE LA BASE")
    print("=" * 50)
    print(f"🏆 Ligues: {LigueArbitrage.objects.count()}")
    print(f"👨‍💼 Administrateurs: {Admin.objects.count()}")
    print(f"⚽ Arbitres: {Arbitre.objects.count()}")
    print(f"🎯 Commissaires: {Commissaire.objects.count()}")
    print("=" * 50)
    print("✅ Initialisation terminée!")

if __name__ == "__main__":
    create_test_data()
