#!/usr/bin/env bash
# build.sh pour Render

# Mettre à jour les packages système
apt-get update

# Installer Python 3.10 et les dépendances nécessaires
apt-get install -y software-properties-common
add-apt-repository ppa:deadsnakes/ppa -y
apt-get update
apt-get install -y python3.10 python3.10-venv python3.10-dev
apt-get install -y libpq-dev build-essential

# Créer un environnement virtuel avec Python 3.10
python3.10 -m venv .venv
source .venv/bin/activate

# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances Python
pip install -r requirements.txt
