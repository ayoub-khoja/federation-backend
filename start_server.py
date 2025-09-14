#!/usr/bin/env python3
"""
Script de démarrage amélioré pour le serveur Django
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Vérifier que toutes les dépendances sont installées"""
    print("🔍 Vérification des dépendances...")
    
    try:
        import django
        print(f"✅ Django {django.get_version()}")
    except ImportError:
        print("❌ Django non installé")
        return False
    
    try:
        import rest_framework
        print("✅ Django REST Framework")
    except ImportError:
        print("❌ Django REST Framework non installé")
        return False
    
    return True

def check_database():
    """Vérifier la base de données"""
    print("\n🗄️ Vérification de la base de données...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
        import django
        django.setup()
        
        from django.db import connection
        from django.core.management import execute_from_command_line
        
        # Test de connexion
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ Connexion à la base de données réussie")
        
        # Vérifier les migrations
        print("🔄 Vérification des migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--check'])
        print("✅ Migrations à jour")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur de base de données: {e}")
        return False

def start_server(host="0.0.0.0", port=8000, production=False):
    """Démarrer le serveur Django"""
    print(f"\n🚀 Démarrage du serveur Django...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Mode: {'PRODUCTION' if production else 'DÉVELOPPEMENT'}")
    
    # Définir les variables d'environnement
    if production:
        os.environ['DJANGO_ENV'] = 'production'
        os.environ['DJANGO_SETTINGS_MODULE'] = 'arbitrage_project.settings_production'
    else:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'arbitrage_project.settings'
    
    # Commandes de démarrage
    if production:
        # En production, utiliser gunicorn
        cmd = [
            'gunicorn',
            'arbitrage_project.wsgi:application',
            f'--bind={host}:{port}',
            '--workers=3',
            '--timeout=120',
            '--keep-alive=2',
            '--max-requests=1000',
            '--max-requests-jitter=100'
        ]
    else:
        # En développement, utiliser runserver
        cmd = ['python', 'manage.py', 'runserver', f'{host}:{port}']
    
    print(f"📝 Commande: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        # Démarrer le serveur
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur demandé par l'utilisateur")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False
    
    return True

def main():
    """Fonction principale"""
    print("🏁 Script de démarrage du serveur Django")
    print("=" * 60)
    
    # Vérifier les arguments
    production = '--production' in sys.argv
    host = '0.0.0.0'
    port = 8000
    
    # Parser les arguments
    for i, arg in enumerate(sys.argv):
        if arg == '--host' and i + 1 < len(sys.argv):
            host = sys.argv[i + 1]
        elif arg == '--port' and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
    
    # Vérifications préliminaires
    if not check_dependencies():
        print("❌ Dépendances manquantes. Installez avec: pip install -r requirements.txt")
        sys.exit(1)
    
    if not check_database():
        print("❌ Problème de base de données. Vérifiez la configuration.")
        sys.exit(1)
    
    # Démarrer le serveur
    success = start_server(host, port, production)
    
    if success:
        print("\n✅ Serveur démarré avec succès!")
    else:
        print("\n❌ Échec du démarrage du serveur")
        sys.exit(1)

if __name__ == "__main__":
    main()



