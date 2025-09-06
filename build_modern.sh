#!/usr/bin/env bash
# build_modern.sh pour Render avec Django 5.0 et psycopg

# Mettre à jour les packages système
apt-get update

# Installer les dépendances nécessaires
apt-get install -y libpq-dev build-essential

# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances Python modernes
pip install -r requirements_modern.txt
