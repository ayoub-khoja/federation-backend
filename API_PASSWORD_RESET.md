# API de Réinitialisation de Mot de Passe

Cette documentation explique comment utiliser l'API de réinitialisation de mot de passe avec envoi d'email via SMTP Gmail.

## Configuration

### 1. Configuration SMTP Gmail

Dans le fichier `settings.py`, configurez vos paramètres Gmail :

```python
# Configuration SMTP Gmail pour l'envoi d'emails
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# Configuration des emails (à remplacer par vos vraies valeurs)
EMAIL_HOST_USER = 'votre-email@gmail.com'  # Votre adresse Gmail
EMAIL_HOST_PASSWORD = 'votre-mot-de-passe-app'  # Mot de passe d'application Gmail
DEFAULT_FROM_EMAIL = 'votre-email@gmail.com'  # Email expéditeur par défaut

# Configuration pour les emails de réinitialisation de mot de passe
PASSWORD_RESET_SETTINGS = {
    'TOKEN_EXPIRY_HOURS': 24,  # Durée de validité du token en heures
    'EMAIL_SUBJECT_PREFIX': '[Fédération Tunisienne de Football] ',
    'FRONTEND_RESET_URL': 'https://votre-frontend.com/reset-password/',  # URL de votre frontend
    'EMAIL_TEMPLATE_NAME': 'password_reset_email.html',
}
```

### 2. Configuration Gmail

Pour utiliser Gmail SMTP, vous devez :

1. **Activer l'authentification à 2 facteurs** sur votre compte Gmail
2. **Générer un mot de passe d'application** :
   - Allez dans Paramètres Google > Sécurité
   - Activez l'authentification à 2 facteurs
   - Générez un mot de passe d'application pour "Mail"
   - Utilisez ce mot de passe dans `EMAIL_HOST_PASSWORD`

## Endpoints API

### 1. Demander une réinitialisation de mot de passe

**POST** `/api/accounts/password-reset/request/`

**Corps de la requête :**
```json
{
    "email": "utilisateur@example.com"
}
```

**Réponse de succès (200) :**
```json
{
    "success": true,
    "message": "Un email de réinitialisation a été envoyé à utilisateur@example.com",
    "user_type": "arbitre",
    "expires_in_hours": 24
}
```

**Réponse d'erreur (404) :**
```json
{
    "success": false,
    "message": "Aucun compte actif trouvé avec cette adresse email.",
    "error_code": "USER_NOT_FOUND"
}
```

### 2. Valider un token de réinitialisation

**GET** `/api/accounts/password-reset/validate/{token}/`

**Réponse de succès (200) :**
```json
{
    "success": true,
    "message": "Token valide",
    "user_info": {
        "email": "utilisateur@example.com",
        "user_type": "arbitre",
        "user_name": "John Doe"
    },
    "expires_at": "2024-01-15T10:30:00Z"
}
```

**Réponse d'erreur (400) :**
```json
{
    "success": false,
    "message": "Token invalide ou expiré",
    "error_code": "INVALID_TOKEN"
}
```

### 3. Confirmer la réinitialisation de mot de passe

**POST** `/api/accounts/password-reset/confirm/`

**Corps de la requête :**
```json
{
    "token": "votre-token-de-reinitialisation",
    "new_password": "nouveauMotDePasse123",
    "confirm_password": "nouveauMotDePasse123"
}
```

**Réponse de succès (200) :**
```json
{
    "success": true,
    "message": "Mot de passe réinitialisé avec succès. Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.",
    "user_type": "arbitre",
    "user_email": "utilisateur@example.com"
}
```

**Réponse d'erreur (400) :**
```json
{
    "success": false,
    "message": "Erreur de validation des données",
    "errors": {
        "confirm_password": "Les mots de passe ne correspondent pas."
    },
    "error_code": "VALIDATION_ERROR"
}
```

## Règles de validation du mot de passe

Le nouveau mot de passe doit respecter les critères suivants :

- **Longueur minimale** : 8 caractères
- **Au moins un chiffre** : Le mot de passe doit contenir au moins un chiffre
- **Au moins une lettre** : Le mot de passe doit contenir au moins une lettre
- **Confirmation** : Les champs `new_password` et `confirm_password` doivent être identiques

## Types d'utilisateurs supportés

L'API supporte la réinitialisation de mot de passe pour tous les types d'utilisateurs :

- **Arbitres** (`arbitre`)
- **Commissaires** (`commissaire`)
- **Administrateurs** (`admin`)

## Sécurité

### Tokens de réinitialisation

- **Durée de validité** : 24 heures par défaut (configurable)
- **Usage unique** : Chaque token ne peut être utilisé qu'une seule fois
- **Invalidation automatique** : Les anciens tokens sont automatiquement invalidés lors de la création d'un nouveau
- **Traçabilité** : Chaque token enregistre l'IP et le User-Agent pour la sécurité

### Email de réinitialisation

L'email contient :
- Un lien sécurisé vers votre frontend avec le token
- Des instructions claires pour l'utilisateur
- Des avertissements de sécurité
- Un design professionnel avec le branding de la Fédération

## Exemple d'utilisation complète

### 1. L'utilisateur demande une réinitialisation

```bash
curl -X POST http://localhost:8000/api/accounts/password-reset/request/ \
  -H "Content-Type: application/json" \
  -d '{"email": "arbitre@example.com"}'
```

### 2. L'utilisateur reçoit l'email et clique sur le lien

Le lien dans l'email pointe vers votre frontend avec le token :
```
https://votre-frontend.com/reset-password/?token=abc123...
```

### 3. Votre frontend valide le token

```bash
curl -X GET http://localhost:8000/api/accounts/password-reset/validate/abc123.../
```

### 4. L'utilisateur soumet le nouveau mot de passe

```bash
curl -X POST http://localhost:8000/api/accounts/password-reset/confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123...",
    "new_password": "nouveauMotDePasse123",
    "confirm_password": "nouveauMotDePasse123"
  }'
```

## Gestion des erreurs

### Codes d'erreur

- `USER_NOT_FOUND` : Aucun compte trouvé avec cet email
- `INVALID_TOKEN` : Token invalide ou expiré
- `VALIDATION_ERROR` : Erreur de validation des données
- `EMAIL_SEND_ERROR` : Erreur lors de l'envoi de l'email
- `ACCOUNT_DISABLED` : Compte désactivé
- `INTERNAL_ERROR` : Erreur interne du serveur

### Logs

Tous les événements sont loggés :
- Envoi d'emails (succès/échec)
- Utilisation des tokens
- Erreurs de validation

## Tests

Pour tester l'API, vous pouvez utiliser les outils suivants :

1. **Postman** : Importez les endpoints et testez les requêtes
2. **curl** : Utilisez les exemples ci-dessus
3. **Frontend** : Intégrez les appels API dans votre interface utilisateur

## Support

En cas de problème :

1. Vérifiez la configuration SMTP Gmail
2. Consultez les logs Django pour les erreurs
3. Vérifiez que l'email de l'utilisateur existe dans la base de données
4. Assurez-vous que le token n'a pas expiré

---

**Note** : Cette API est sécurisée et suit les meilleures pratiques de sécurité pour la réinitialisation de mots de passe.













