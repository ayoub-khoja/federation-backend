# API Backend - Direction Nationale de l'Arbitrage

## 🚀 Installation et Configuration

### 1. Prérequis
- Python 3.8 ou plus récent
- pip (gestionnaire de paquets Python)
- Optionnel : PostgreSQL pour la production

### 2. Installation des dépendances

```bash
# Dans le dossier backend
cd backend

# Créer un environnement virtuel (recommandé)
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows:
venv\Scripts\activate
# Sur macOS/Linux:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. Configuration de la base de données

#### Option A: SQLite (par défaut - pour le développement)
Aucune configuration supplémentaire requise. La base de données sera créée automatiquement.

#### Option B: PostgreSQL (pour la production)
1. Installer PostgreSQL sur votre système
2. Créer une base de données :
```sql
CREATE DATABASE arbitrage_db;
CREATE USER arbitrage_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE arbitrage_db TO arbitrage_user;
```
3. Modifier `settings.py` pour utiliser PostgreSQL (décommenter la section PostgreSQL)

### 4. Configuration d'environnement

```bash
# Copier le fichier d'exemple
cp env.example .env

# Modifier le fichier .env avec vos configurations
```

### 5. Migrations de la base de données

```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate
```

### 6. Créer un super utilisateur

```bash
python manage.py createsuperuser
```

Vous devrez entrer :
- Numéro de téléphone : +21612345678 (format obligatoire)
- Prénom et Nom
- Mot de passe

### 7. Lancer le serveur de développement

```bash
python manage.py runserver

# Pour accès mobile (remplacez par votre IP locale)
python manage.py runserver 0.0.0.0:8000
```

## 📡 Endpoints API

### Authentification
- `POST /api/auth/login/` - Connexion
- `POST /api/auth/register/` - Inscription
- `POST /api/auth/logout/` - Déconnexion
- `GET /api/auth/profile/` - Profil utilisateur
- `PUT /api/auth/profile/` - Modifier le profil
- `POST /api/auth/change-password/` - Changer le mot de passe

### Gestion des matchs
- `GET /api/matches/` - Liste des matchs
- `POST /api/matches/` - Créer un match
- `GET /api/matches/{id}/` - Détails d'un match
- `PUT /api/matches/{id}/` - Modifier un match
- `DELETE /api/matches/{id}/` - Supprimer un match
- `POST /api/matches/{id}/complete/` - Marquer comme terminé
- `GET /api/matches/statistics/` - Statistiques
- `GET /api/matches/upcoming/` - Prochains matchs
- `GET /api/matches/recent/` - Matchs récents

### Santé de l'API
- `GET /api/auth/health/` - Vérifier le fonctionnement

## 🔗 Format des données

### Connexion
```json
{
  "phone_number": "+21612345678",
  "password": "votre_mot_de_passe"
}
```

### Inscription
```json
{
  "phone_number": "+21612345678",
  "password": "votre_mot_de_passe",
  "password_confirm": "votre_mot_de_passe",
  "first_name": "Ahmed",
  "last_name": "Ben Ali",
  "grade": "national",
  "league": "ligue1"
}
```

### Création de match
```json
{
  "match_type": "ligue1",
  "category": "senior",
  "stadium": "Stade Olympique de Radès",
  "match_date": "2024-01-15",
  "match_time": "15:00",
  "home_team": "Club Africain",
  "away_team": "Espérance de Tunis",
  "description": "Match de championnat"
}
```

## 🛡️ Sécurité

- Authentification JWT avec refresh tokens
- CORS configuré pour le frontend
- Validation des numéros de téléphone tunisiens
- Permissions basées sur l'utilisateur connecté

## 📱 Test avec le frontend

1. S'assurer que le backend fonctionne sur `http://localhost:8000`
2. Le frontend sur `http://localhost:3000`
3. Les appels API sont automatiquement routés grâce à la configuration CORS

## 🔧 Administration

Accédez à l'interface d'administration sur `http://localhost:8000/admin/` avec votre compte super utilisateur.

## 📊 Modèles de données

### Arbitre (Utilisateur personnalisé)
- Authentification par numéro de téléphone
- Informations personnelles et professionnelles
- Grades et ligues d'arbitrage
- Photo de profil

### Match
- Informations du match (équipes, stade, date/heure)
- Type et catégorie de match
- Score et statut
- Rapport et incidents
- Feuille de match (upload de fichier)

### MatchEvent
- Événements du match (cartons, buts, etc.)
- Associé à un match et un joueur
- Minute de l'événement

## 🚨 Dépannage

### Problème de migration
```bash
python manage.py migrate --run-syncdb
```

### Réinitialiser la base de données
```bash
# ATTENTION: Cela supprime toutes les données
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Erreur CORS
Vérifiez que l'URL du frontend est bien dans `CORS_ALLOWED_ORIGINS` dans `settings.py`


































