#!/usr/bin/env bash
# build.sh pour Render

# Mettre à jour les packages système
apt-get update

# Installer les dépendances nécessaires pour psycopg2
apt-get install -y libpq-dev

# Installer les dépendances Python
pip install -r requirements.txt
