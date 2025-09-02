# API de Mise à Jour du Profil Arbitre

## Description
Cette API permet aux arbitres de mettre à jour tous les champs de leur profil de manière complète ou partielle.

## Endpoint
```
PUT/PATCH /api/accounts/arbitres/profile/update/
```

## Authentification
- **Type**: JWT Bearer Token
- **Header**: `Authorization: Bearer <access_token>`
- **Permissions**: Seuls les arbitres authentifiés peuvent modifier leur propre profil

## Champs Modifiables

### Informations Personnelles
- `first_name` (string) - Prénom
- `last_name` (string) - Nom
- `email` (string, optionnel) - Adresse email
- `birth_date` (date, format: YYYY-MM-DD) - Date de naissance
- `birth_place` (string, optionnel) - Lieu de naissance
- `address` (string, optionnel) - Adresse complète
- `cin` (string, optionnel) - Numéro CIN (unique)
- `profile_photo` (file, optionnel) - Photo de profil

### Informations Professionnelles
- `role` (string) - Rôle: `arbitre` ou `assistant`
- `grade` (string) - Grade d'arbitrage:
  - `candidat`
  - `3eme_serie`
  - `2eme_serie`
  - `1ere_serie`
  - `federale`
- `ligue` (integer, optionnel) - ID de la ligue d'arbitrage

## Exemples d'Utilisation

### 1. Mise à Jour Complète
```bash
curl -X PATCH "http://localhost:8000/api/accounts/arbitres/profile/update/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Ahmed",
    "last_name": "Ben Ali",
    "email": "ahmed.benali@example.com",
    "address": "123 Rue de la Paix, Tunis",
    "birth_date": "1990-05-15",
    "birth_place": "Tunis",
    "cin": "12345678",
    "role": "arbitre",
    "grade": "1ere_serie",
    "ligue": 1
  }'
```

### 2. Mise à Jour Partielle (seulement l'email)
```bash
curl -X PATCH "http://localhost:8000/api/accounts/arbitres/profile/update/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nouveau.email@example.com"
  }'
```

### 3. Mise à Jour avec Photo de Profil
```bash
curl -X PATCH "http://localhost:8000/api/accounts/arbitres/profile/update/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "profile_photo=@/chemin/vers/photo.jpg" \
  -F "first_name=Ahmed" \
  -F "last_name=Ben Ali"
```

## Réponses

### Succès (200 OK)
```json
{
  "success": true,
  "message": "Profil arbitre mis à jour avec succès",
  "arbitre": {
    "id": 30,
    "phone_number": "+21699999999",
    "email": "ahmed.benali@example.com",
    "first_name": "Ahmed",
    "last_name": "Ben Ali",
    "role": "arbitre",
    "grade": "1ere_serie",
    "ligue": 1,
    "ligue_nom": "Ligue de Tunis",
    "address": "123 Rue de la Paix, Tunis",
    "birth_date": "1990-05-15",
    "birth_place": "Tunis",
    "cin": "12345678",
    "profile_photo": "http://localhost:8000/media/profiles/photo.jpg",
    "date_joined": "2025-09-02T16:15:51.089380+01:00",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false
  },
  "updated_fields": [
    "first_name",
    "last_name",
    "email",
    "address",
    "birth_date",
    "birth_place",
    "cin",
    "role",
    "grade",
    "ligue"
  ]
}
```

### Erreur de Validation (400 Bad Request)
```json
{
  "success": false,
  "message": "Erreur de validation des données",
  "errors": {
    "cin": "Ce numéro CIN est déjà utilisé par un autre arbitre.",
    "grade": "Sélectionnez un choix valide. candidat n'est pas un des choix disponibles."
  },
  "error_code": "VALIDATION_ERROR"
}
```

### Accès Non Autorisé (403 Forbidden)
```json
{
  "success": false,
  "message": "Accès non autorisé - Seuls les arbitres peuvent modifier leur profil",
  "error_code": "ACCESS_DENIED"
}
```

### Erreur Serveur (500 Internal Server Error)
```json
{
  "success": false,
  "message": "Erreur interne du serveur lors de la mise à jour",
  "error": "Détails de l'erreur",
  "error_code": "INTERNAL_ERROR"
}
```

## Validations

### CIN (Numéro d'Identité)
- Doit être unique dans la base de données
- Validation automatique de l'unicité

### Ligue
- Doit exister et être active
- Validation automatique de l'existence

### Grade
- Doit être un des choix valides définis dans le modèle

### Rôle
- Doit être `arbitre` ou `assistant`

## Notes Importantes

1. **Mise à Jour Partielle**: L'API supporte la mise à jour partielle avec `PATCH`
2. **Champs en Lecture Seule**: Les champs suivants ne peuvent pas être modifiés :
   - `id`
   - `phone_number`
   - `date_joined`
   - `is_active`
   - `is_staff`
   - `is_superuser`
3. **Authentification**: Seul l'arbitre propriétaire du profil peut le modifier
4. **Validation**: Toutes les validations sont appliquées automatiquement
5. **Réponse Complète**: La réponse inclut toujours le profil complet mis à jour

## Codes d'Erreur

- `ACCESS_DENIED`: Accès non autorisé
- `VALIDATION_ERROR`: Erreur de validation des données
- `INTERNAL_ERROR`: Erreur interne du serveur

## Test de l'API

Un script de test est disponible dans `test_update_profile_api.py` pour vérifier le bon fonctionnement de l'API.
