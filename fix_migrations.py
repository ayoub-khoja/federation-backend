#!/usr/bin/env python
"""
Script pour résoudre les problèmes de migration automatiquement
"""
import os
import django
from pathlib import Path

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import LigueArbitrage

def create_migration_file():
    """Créer un fichier de migration manuel"""
    
    # 1. Créer d'abord une ligue
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
    
    # 2. Créer le fichier de migration
    migration_content = f"""
from django.db import migrations, models
import django.db.models.deletion

def create_default_ligue(apps, schema_editor):
    LigueArbitrage = apps.get_model('accounts', 'LigueArbitrage')
    ligue, created = LigueArbitrage.objects.get_or_create(
        nom="Ligue de Tunis",
        defaults={{
            'region': 'Tunis',
            'description': 'Ligue principale de Tunis',
            'is_active': True
        }}
    )

def reverse_create_default_ligue(apps, schema_editor):
    LigueArbitrage = apps.get_model('accounts', 'LigueArbitrage')
    try:
        ligue = LigueArbitrage.objects.get(nom="Ligue de Tunis")
        ligue.delete()
    except LigueArbitrage.DoesNotExist:
        pass

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0006_alter_arbitre_options_remove_arbitre_user_type_and_more'),
    ]

    operations = [
        # 1. Renommer le champ active en is_active
        migrations.RenameField(
            model_name='liguearbitrage',
            old_name='active',
            new_name='is_active',
        ),
        
        # 2. Créer la ligue par défaut
        migrations.RunPython(
            create_default_ligue,
            reverse_create_default_ligue,
        ),
        
        # 3. Ajouter le champ ligue à arbitre avec la ligue par défaut
        migrations.AddField(
            model_name='arbitre',
            name='ligue',
            field=models.ForeignKey(
                default=1,  # ID de la ligue créée
                on_delete=django.db.models.deletion.CASCADE,
                to='accounts.liguearbitrage',
                verbose_name="Ligue d'arbitrage"
            ),
            preserve_default=False,
        ),
        
        # 4. Ajouter le champ ligue à commissaire avec la ligue par défaut
        migrations.AddField(
            model_name='commissaire',
            name='ligue',
            field=models.ForeignKey(
                default=1,  # ID de la ligue créée
                on_delete=django.db.models.deletion.CASCADE,
                to='accounts.liguearbitrage',
                verbose_name="Ligue d'arbitrage"
            ),
            preserve_default=False,
        ),
    ]
"""
    
    # Créer le fichier de migration
    migration_file = Path("accounts/migrations/0007_fix_models.py")
    migration_file.parent.mkdir(exist_ok=True)
    
    with open(migration_file, 'w', encoding='utf-8') as f:
        f.write(migration_content)
    
    print(f"✅ Fichier de migration créé: {migration_file}")
    return True

if __name__ == "__main__":
    print("🔧 Création de la migration automatique...")
    create_migration_file()
    print("✅ Migration créée avec succès!")
    print("\n📋 Prochaines étapes:")
    print("1. Appliquer la migration: python manage.py migrate")
    print("2. Initialiser la base: python init_database.py")
