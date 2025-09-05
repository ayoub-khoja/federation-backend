# API Excuses d'Arbitres par Date

Ce document décrit les APIs pour consulter les excuses d'arbitres filtrées par date.

## Endpoints Disponibles

### 1. Excuses Passées par Date
**URL:** `GET /api/matches/excuses/passees/`

**Description:** Récupère toutes les excuses d'arbitres dont la date de fin est antérieure à la date spécifiée.

**Paramètres:**
- `date` (requis): Date de référence au format YYYY-MM-DD

**Exemple de requête:**
```bash
GET /api/matches/excuses/passees/?date=2024-01-15
```

**Exemple de réponse:**
```json
{
    "success": true,
    "message": "2 excuse(s) passée(s) trouvée(s) pour le 2024-01-15",
    "date_cible": "2024-01-15",
    "excuses_passees": [
        {
            "id": 1,
            "nom_arbitre": "Dupont",
            "prenom_arbitre": "Jean",
            "date_debut": "2024-01-10",
            "date_fin": "2024-01-12",
            "cause": "Maladie",
            "piece_jointe": null,
            "created_at": "2024-01-09T10:30:00Z",
            "updated_at": "2024-01-09T10:30:00Z"
        }
    ]
}
```

### 2. Excuses en Cours par Date
**URL:** `GET /api/matches/excuses/en-cours/`

**Description:** Récupère toutes les excuses d'arbitres qui sont actives à la date spécifiée (date_debut ≤ date_cible ≤ date_fin).

**Paramètres:**
- `date` (requis): Date de référence au format YYYY-MM-DD

**Exemple de requête:**
```bash
GET /api/matches/excuses/en-cours/?date=2024-01-15
```

**Exemple de réponse:**
```json
{
    "success": true,
    "message": "1 excuse(s) en cours trouvée(s) pour le 2024-01-15",
    "date_cible": "2024-01-15",
    "excuses_en_cours": [
        {
            "id": 2,
            "nom_arbitre": "Martin",
            "prenom_arbitre": "Pierre",
            "date_debut": "2024-01-14",
            "date_fin": "2024-01-16",
            "cause": "Blessure",
            "piece_jointe": null,
            "created_at": "2024-01-13T14:20:00Z",
            "updated_at": "2024-01-13T14:20:00Z"
        }
    ]
}
```

### 3. Excuses à Venir par Date
**URL:** `GET /api/matches/excuses/a-venir/`

**Description:** Récupère toutes les excuses d'arbitres dont la date de début est postérieure à la date spécifiée.

**Paramètres:**
- `date` (requis): Date de référence au format YYYY-MM-DD

**Exemple de requête:**
```bash
GET /api/matches/excuses/a-venir/?date=2024-01-15
```

**Exemple de réponse:**
```json
{
    "success": true,
    "message": "1 excuse(s) à venir trouvée(s) pour le 2024-01-15",
    "date_cible": "2024-01-15",
    "excuses_a_venir": [
        {
            "id": 3,
            "nom_arbitre": "Bernard",
            "prenom_arbitre": "Paul",
            "date_debut": "2024-01-20",
            "date_fin": "2024-01-22",
            "cause": "Voyage",
            "piece_jointe": null,
            "created_at": "2024-01-10T09:15:00Z",
            "updated_at": "2024-01-10T09:15:00Z"
        }
    ]
}
```

## Codes de Statut HTTP

- **200 OK:** Requête réussie
- **400 Bad Request:** Paramètre date manquant ou format invalide

## Gestion des Erreurs

### Date manquante
```json
{
    "success": false,
    "message": "Paramètre date requis (format: YYYY-MM-DD)"
}
```

### Format de date invalide
```json
{
    "success": false,
    "message": "Format de date invalide. Utilisez YYYY-MM-DD"
}
```

## Exemples d'Utilisation

### Avec cURL
```bash
# Excuses passées
curl "http://localhost:8000/api/matches/excuses/passees/?date=2024-01-15"

# Excuses en cours
curl "http://localhost:8000/api/matches/excuses/en-cours/?date=2024-01-15"

# Excuses à venir
curl "http://localhost:8000/api/matches/excuses/a-venir/?date=2024-01-15"
```

### Avec JavaScript/Fetch
```javascript
// Excuses passées
fetch('/api/matches/excuses/passees/?date=2024-01-15')
    .then(response => response.json())
    .then(data => console.log(data));

// Excuses en cours
fetch('/api/matches/excuses/en-cours/?date=2024-01-15')
    .then(response => response.json())
    .then(data => console.log(data));

// Excuses à venir
fetch('/api/matches/excuses/a-venir/?date=2024-01-15')
    .then(response => response.json())
    .then(data => console.log(data));
```

### Avec Python/Requests
```python
import requests

# Excuses passées
response = requests.get('http://localhost:8000/api/matches/excuses/passees/', 
                       params={'date': '2024-01-15'})
print(response.json())

# Excuses en cours
response = requests.get('http://localhost:8000/api/matches/excuses/en-cours/', 
                       params={'date': '2024-01-15'})
print(response.json())

# Excuses à venir
response = requests.get('http://localhost:8000/api/matches/excuses/a-venir/', 
                       params={'date': '2024-01-15'})
print(response.json())
```

## Notes Importantes

1. **Format de date:** Toutes les dates doivent être au format ISO 8601 (YYYY-MM-DD)
2. **Fuseau horaire:** Les dates sont traitées en UTC
3. **Tri:** 
   - Excuses passées: triées par date de fin décroissante
   - Excuses en cours: triées par date de création décroissante
   - Excuses à venir: triées par date de début croissante
4. **Permissions:** Ces endpoints sont accessibles sans authentification (permissions.AllowAny)

## Cas d'Usage

- **Planification:** Utiliser les excuses à venir pour planifier les matchs
- **Suivi:** Utiliser les excuses en cours pour le suivi quotidien
- **Historique:** Utiliser les excuses passées pour l'analyse historique
- **Rapports:** Générer des rapports par période en utilisant différentes dates de référence


