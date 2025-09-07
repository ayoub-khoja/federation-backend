#!/usr/bin/env bash
# Script de build pour Render.com

echo "🚀 Début du build pour la production..."

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# Vérifier la configuration
echo "🔍 Vérification de la configuration..."
python -c "import django; print(f'Django {django.get_version()} installé')"

# Appliquer les migrations
echo "🗄️ Application des migrations..."
python manage.py migrate --noinput

# Collecter les fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Vérifier la configuration de production
echo "🔧 Vérification de la configuration de production..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings_production')
import django
django.setup()
from django.conf import settings
print(f'✅ DEBUG: {settings.DEBUG}')
print(f'✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
print(f'✅ CORS_ALLOW_ALL_ORIGINS: {settings.CORS_ALLOW_ALL_ORIGINS}')
"

# Test de connectivité de la base de données
echo "🔗 Test de connexion à la base de données..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings_production')
import django
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT 1')
    print('✅ Connexion à la base de données réussie')
"

echo "✅ Build terminé avec succès !"
echo "🌐 Le serveur est prêt à être déployé"
