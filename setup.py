#!/usr/bin/env python
"""
Script de configuration automatique pour le backend Django
"""
import os
import sys
import subprocess
import secrets

def run_command(command, description):
    """Exécuter une commande avec gestion d'erreur"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Terminé")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de {description}")
        print(f"Erreur: {e.stderr}")
        return False

def create_env_file():
    """Créer le fichier .env avec une clé secrète générée"""
    if os.path.exists('.env'):
        print("⚠️  Le fichier .env existe déjà, ignoré")
        return
    
    secret_key = secrets.token_urlsafe(50)
    env_content = f"""# Configuration d'environnement Django
SECRET_KEY={secret_key}
DEBUG=True

# Base de données (SQLite par défaut)
# Décommentez pour PostgreSQL :
# DB_NAME=arbitrage_db
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    print("✅ Fichier .env créé avec une clé secrète générée")

def main():
    """Script principal de configuration"""
    print("🚀 Configuration automatique du backend Django")
    print("=" * 50)
    
    # Vérifier Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 ou plus récent est requis")
        sys.exit(1)
    
    # Créer le fichier .env
    create_env_file()
    
    # Installer les dépendances
    if not run_command("pip install -r requirements.txt", "Installation des dépendances"):
        print("❌ Impossible d'installer les dépendances")
        sys.exit(1)
    
    # Migrations
    if not run_command("python manage.py makemigrations", "Création des migrations"):
        print("❌ Erreur lors de la création des migrations")
        sys.exit(1)
    
    if not run_command("python manage.py migrate", "Application des migrations"):
        print("❌ Erreur lors de l'application des migrations")
        sys.exit(1)
    
    print("\n🎉 Configuration terminée avec succès !")
    print("\n📋 Prochaines étapes :")
    print("1. Créer un super utilisateur :")
    print("   python manage.py createsuperuser")
    print("\n2. Lancer le serveur :")
    print("   python manage.py runserver")
    print("\n3. Pour accès mobile :")
    print("   python manage.py runserver 0.0.0.0:8000")
    print("\n4. Interface admin :")
    print("   http://localhost:8000/admin/")
    print("\n5. API de santé :")
    print("   http://localhost:8000/api/auth/health/")

if __name__ == "__main__":
    main()













