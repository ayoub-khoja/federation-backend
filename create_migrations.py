#!/usr/bin/env python
"""
Script pour créer et appliquer les migrations des nouveaux modèles d'utilisateurs
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.db import DEFAULT_DB_ALIAS

def check_migrations():
    """Vérifie s'il y a des migrations en attente"""
    connection = django.db.connections[DEFAULT_DB_ALIAS]
    connection.ensure_connection()
    
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    
    if plan:
        print(f"Il y a {len(plan)} migration(s) en attente:")
        for migration, backwards in plan:
            print(f"  - {migration}")
        return True
    else:
        print("Aucune migration en attente.")
        return False

def create_migrations():
    """Crée les fichiers de migration"""
    print("Création des fichiers de migration...")
    execute_from_command_line(['manage.py', 'makemigrations', 'accounts'])

def apply_migrations():
    """Applique les migrations"""
    print("Application des migrations...")
    execute_from_command_line(['manage.py', 'migrate'])

def create_superuser():
    """Crée un super utilisateur administrateur"""
    print("Création d'un super utilisateur administrateur...")
    execute_from_command_line(['manage.py', 'createsuperuser'])

def main():
    """Fonction principale"""
    print("=== Gestion des migrations pour les nouveaux modèles d'utilisateurs ===\n")
    
    # Vérifier les migrations en attente
    if check_migrations():
        # Créer les migrations
        create_migrations()
        
        # Appliquer les migrations
        apply_migrations()
        
        # Créer un super utilisateur
        create_superuser()
        
        print("\n=== Migration terminée avec succès! ===")
    else:
        print("Aucune action nécessaire.")

if __name__ == '__main__':
    main()
