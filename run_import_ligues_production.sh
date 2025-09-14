#!/bin/bash

# Script pour importer les ligues en production
# Utilise la commande Django existante avec la configuration de production

echo "🏛️  IMPORTATION DES LIGUES D'ARBITRAGE - PRODUCTION"
echo "=================================================="

# Vérifier que nous sommes dans le bon répertoire
if [ ! -f "manage.py" ]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis le répertoire backend"
    exit 1
fi

# Vérifier que le fichier YAML existe
if [ ! -f "data/ligues.yaml" ]; then
    echo "❌ Erreur: Le fichier data/ligues.yaml n'existe pas"
    exit 1
fi

echo "🔧 Configuration: PRODUCTION"
echo "🗄️ Base de données: PostgreSQL"
echo "📁 Fichier source: data/ligues.yaml"
echo ""

# Demander confirmation
read -p "❓ Voulez-vous continuer avec l'importation? (oui/non): " response
if [[ ! "$response" =~ ^(oui|o|yes|y)$ ]]; then
    echo "❌ Importation annulée par l'utilisateur"
    exit 0
fi

echo ""
echo "🚀 Lancement de l'importation..."
echo ""

# Exécuter la commande Django avec la configuration de production
DJANGO_SETTINGS_MODULE=arbitrage_project.settings_production python manage.py import_ligues --file=data/ligues.yaml --force

# Vérifier le code de retour
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Importation terminée avec succès!"
else
    echo ""
    echo "❌ Erreur lors de l'importation!"
    exit 1
fi
