# API Tarification des Matchs

## Description
Cette API permet de gérer les tarifs des matchs selon le type de compétition, la division, le type de match et le rôle d'arbitrage.

## Modèle de données

### TarificationMatch
- **competition**: Type de compétition (championnat, coupe_tunisie_seniors, etc.)
- **division**: Division (seniors, jeunes, feminin, cadettes)
- **type_match**: Type de match (ligue1, ligue2, c1, c2, etc.)
- **role**: Rôle d'arbitrage (arbitre, assistant, 4eme_arbitre, commissaire)
- **tarif**: Montant en dinars tunisiens (DecimalField)
- **devise**: Devise (par défaut TND)
- **is_active**: Statut actif/inactif

## Endpoints disponibles

### 1. Lister toutes les tarifications
**GET** `/api/matches/tarification/`

**Paramètres de filtrage (query parameters):**
- `competition`: Filtrer par compétition
- `division`: Filtrer par division
- `type_match`: Filtrer par type de match
- `role`: Filtrer par rôle
- `is_active`: Filtrer par statut actif (true/false)

**Exemple de requête:**
```bash
GET /api/matches/tarification/?competition=championnat&type_match=ligue1
```

**Réponse:**
```json
[
    {
        "id": 1,
        "competition_display": "Championnat",
        "division_display": "Seniors",
        "type_match_display": "Ligue 1",
        "role_display": "Arbitre",
        "tarif_formatted": "400.000 TND",
        "is_active": true
    }
]
```

### 2. Récupérer une tarification spécifique
**GET** `/api/matches/tarification/{id}/`

**Réponse:**
```json
{
    "id": 1,
    "competition": "championnat",
    "competition_display": "Championnat",
    "division": "seniors",
    "division_display": "Seniors",
    "type_match": "ligue1",
    "type_match_display": "Ligue 1",
    "role": "arbitre",
    "role_display": "Arbitre",
    "tarif": "400.000",
    "tarif_formatted": "400.000 TND",
    "devise": "TND",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### 3. Créer une nouvelle tarification
**POST** `/api/matches/tarification/create/`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
    "competition": "championnat",
    "division": "seniors",
    "type_match": "ligue1",
    "role": "arbitre",
    "tarif": "400.000",
    "devise": "TND",
    "is_active": true
}
```

### 4. Modifier une tarification
**PUT/PATCH** `/api/matches/tarification/{id}/update/`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
    "tarif": "450.000",
    "is_active": true
}
```

### 5. Récupérer les tarifications par compétition
**GET** `/api/matches/tarification/competition/{competition}/`

**Exemple:**
```bash
GET /api/matches/tarification/competition/championnat/
```

**Réponse:**
```json
{
    "success": true,
    "message": "Tarifications trouvées pour championnat",
    "competition": "championnat",
    "count": 24,
    "tarifications": [...]
}
```

### 6. Récupérer les tarifications par type de match
**GET** `/api/matches/tarification/competition/{competition}/type/{type_match}/`

**Exemple:**
```bash
GET /api/matches/tarification/competition/championnat/type/ligue1/
```

### 7. Récupérer la tarification d'un rôle spécifique
**GET** `/api/matches/tarification/competition/{competition}/type/{type_match}/role/{role}/`

**Exemple:**
```bash
GET /api/matches/tarification/competition/championnat/type/ligue1/role/arbitre/
```

**Réponse:**
```json
{
    "success": true,
    "message": "Tarification trouvée",
    "tarification": {
        "id": 1,
        "competition": "championnat",
        "competition_display": "Championnat",
        "division": "seniors",
        "division_display": "Seniors",
        "type_match": "ligue1",
        "type_match_display": "Ligue 1",
        "role": "arbitre",
        "role_display": "Arbitre",
        "tarif": "400.000",
        "tarif_formatted": "400.000 TND",
        "devise": "TND",
        "is_active": true
    }
}
```

## Valeurs possibles

### Compétitions
- `championnat`: Championnat
- `coupe_tunisie_seniors`: Coupe de Tunisie Seniors
- `coupe_tunisie_jeunes`: Coupe de Tunisie Jeunes
- `super_coupe`: Super Coupe de Tunisie
- `matchs_amicaux`: Matchs Amicaux

### Divisions
- `seniors`: Seniors
- `jeunes`: Jeunes
- `feminin`: Féminin
- `cadettes`: Cadettes

### Types de match
- `ligue1`: Ligue 1
- `ligue2`: Ligue 2
- `c1`: C1
- `c2`: C2
- `ff`: FF
- `reg`: Régional
- `1_8`: 1/8 de finale
- `1_4`: 1/4 de finale
- `1_2`: 1/2 de finale
- `finale`: Finale
- `u21_u19`: U21/U19
- `u17_u16_u15_u14`: U17/U16/U15/U14
- `feminin_cadettes`: Féminin Cadettes
- `super_coupe_seniors`: Super Coupe Seniors
- `seniors_amical`: Seniors Amical
- `u21_u19_amical`: U21/U19 Amical
- `u15_u14_amical`: U15/U14 Amical
- `eq_nat_vs_club_seniors`: Équipe Nationale vs Club Seniors
- `eq_nat_vs_club_u21_u19`: Équipe Nationale vs Club U21/U19
- `eq_nat_vs_club_u15_u14`: Équipe Nationale vs Club U15/U14

### Rôles
- `arbitre`: Arbitre
- `assistant`: Assistant
- `4eme_arbitre`: 4ème Arbitre
- `commissaire`: Commissaire

## Exemples d'utilisation

### Récupérer tous les tarifs de Ligue 1
```bash
curl "http://localhost:8000/api/matches/tarification/?competition=championnat&type_match=ligue1"
```

### Récupérer tous les tarifs des jeunes
```bash
curl "http://localhost:8000/api/matches/tarification/?division=jeunes"
```

### Récupérer tous les tarifs d'arbitre
```bash
curl "http://localhost:8000/api/matches/tarification/?role=arbitre"
```

### Récupérer les tarifs de la Coupe de Tunisie Seniors
```bash
curl "http://localhost:8000/api/matches/tarification/competition/coupe_tunisie_seniors/"
```

## Gestion des erreurs

### 404 - Tarification non trouvée
```json
{
    "success": false,
    "message": "Tarification non trouvée"
}
```

### 400 - Données invalides
```json
{
    "success": false,
    "message": "Une tarification existe déjà pour cette combinaison de compétition, division, type de match et rôle."
}
```

### 500 - Erreur serveur
```json
{
    "success": false,
    "message": "Erreur lors de la récupération des tarifications: <détails>"
}
```

## Notes importantes

1. **Authentification**: Les opérations de création, modification et suppression nécessitent une authentification JWT.

2. **Unicité**: Chaque combinaison de compétition, division, type de match et rôle doit être unique.

3. **Devise**: Par défaut, tous les tarifs sont en dinars tunisiens (TND).

4. **Statut actif**: Seules les tarifications actives (`is_active=true`) sont retournées par les APIs de consultation.

5. **Filtrage**: Tous les endpoints de liste supportent le filtrage par les différents champs.

6. **Pagination**: Les endpoints de liste supportent la pagination Django REST Framework standard.

