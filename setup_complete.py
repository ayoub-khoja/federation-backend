#!/usr/bin/env python
"""
Script de setup automatique complet pour le système d'arbitrage
"""
import os
import sys
import subprocess
import django
from pathlib import Path

def run_command(command, description):
    """Exécuter une commande et afficher le résultat"""
    print(f"\n🔧 {description}...")
    print(f"   Commande: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print(f"   ✅ Succès: {description}")
            if result.stdout:
                print(f"   📤 Sortie: {result.stdout.strip()}")
        else:
            print(f"   ❌ Erreur: {description}")
            if result.stderr:
                print(f"   📤 Erreur: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False
    
    return True

def setup_database():
    """Configurer la base de données automatiquement"""
    print("🚀 SETUP AUTOMATIQUE COMPLET")
    print("=" * 60)
    
    # 1. Créer les migrations
    print("\n📋 ÉTAPE 1: Création des migrations")
    print("-" * 40)
    
    # Créer un fichier de migration automatique
    migration_content = """
from django.db import migrations, models
import django.utils.timezone

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0006_alter_arbitre_options_remove_arbitre_user_type_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='liguearbitrage',
            old_name='active',
            new_name='is_active',
        ),
        migrations.AddField(
            model_name='arbitre',
            name='date_debut',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='commissaire',
            name='date_debut',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
"""
    
    # Créer le fichier de migration
    migration_file = Path("accounts/migrations/0007_auto_update.py")
    migration_file.parent.mkdir(exist_ok=True)
    
    with open(migration_file, 'w', encoding='utf-8') as f:
        f.write(migration_content)
    
    print("   ✅ Fichier de migration créé automatiquement")
    
    # 2. Appliquer les migrations
    print("\n📋 ÉTAPE 2: Application des migrations")
    print("-" * 40)
    
    if not run_command("python manage.py migrate", "Application des migrations"):
        print("   ❌ Échec des migrations")
        return False
    
    # 3. Initialiser la base de données
    print("\n📋 ÉTAPE 3: Initialisation de la base")
    print("-" * 40)
    
    # Configuration Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
    django.setup()
    
    from accounts.models import LigueArbitrage, Arbitre, Commissaire, Admin
    from django.contrib.auth.hashers import make_password
    
    try:
        # Créer une ligue de test
        ligue, created = LigueArbitrage.objects.get_or_create(
            nom="Ligue de Tunis",
            defaults={
                'region': 'Tunis',
                'description': 'Ligue principale de Tunis',
                'is_active': True
            }
        )
        
        if created:
            print(f"   ✅ Ligue créée: {ligue.nom} - {ligue.region}")
        else:
            print(f"   ℹ️ Ligue existante: {ligue.nom} - {ligue.region}")
        
        # Créer un administrateur de test
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
            print(f"   ✅ Administrateur créé: {admin.first_name} {admin.last_name}")
        else:
            print(f"   ℹ️ Administrateur existant: {admin.first_name} {admin.last_name}")
        
        # Créer un arbitre de test
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
            print(f"   ✅ Arbitre créé: {arbitre.first_name} {arbitre.last_name}")
        else:
            print(f"   ℹ️ Arbitre existant: {arbitre.first_name} {arbitre.last_name}")
        
        # Créer un commissaire de test
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
            print(f"   ✅ Commissaire créé: {commissaire.first_name} {commissaire.last_name}")
        else:
            print(f"   ℹ️ Commissaire existant: {commissaire.first_name} {commissaire.last_name}")
        
        print("\n   📊 RÉSUMÉ DE LA BASE")
        print(f"   🏆 Ligues: {LigueArbitrage.objects.count()}")
        print(f"   👨‍💼 Administrateurs: {Admin.objects.count()}")
        print(f"   ⚽ Arbitres: {Arbitre.objects.count()}")
        print(f"   🎯 Commissaires: {Commissaire.objects.count()}")
        
    except Exception as e:
        print(f"   ❌ Erreur lors de l'initialisation: {e}")
        return False
    
    # 4. Tester la connexion
    print("\n📋 ÉTAPE 4: Test de connexion")
    print("-" * 40)
    
    if not run_command("python test_connection.py", "Test de connexion"):
        print("   ❌ Échec du test de connexion")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 SETUP TERMINÉ AVEC SUCCÈS!")
    print("=" * 60)
    
    print("\n📱 INFORMATIONS DE CONNEXION:")
    print("👨‍💼 ADMIN (Interface Web):")
    print("   📱 Téléphone: +21611111111")
    print("   🔑 Mot de passe: admin123456")
    print("   🌐 URL: http://localhost:3001")
    
    print("\n⚽ ARBITRE (Interface Mobile):")
    print("   📱 Téléphone: +21622222222")
    print("   🔑 Mot de passe: arbitre123456")
    print("   📱 URL: http://localhost:3000")
    
    print("\n🎯 COMMISSAIRE (Interface Mobile de Test):")
    print("   📱 Téléphone: +21633333333")
    print("   🔑 Mot de passe: commissaire123456")
    print("   🐍 Script: python commissaire_mobile_test.py")
    
    print("\n🚀 Prochaines étapes:")
    print("1. Démarrer Django: python manage.py runserver")
    print("2. Démarrer le frontend admin: cd ../frontend-admin && npm run dev")
    print("3. Démarrer le frontend mobile: cd ../frontend && npm run dev")
    
    return True

if __name__ == "__main__":
    setup_database()
