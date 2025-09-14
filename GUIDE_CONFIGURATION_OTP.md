# 🔐 Guide de Configuration - Système OTP + Lien Sécurisé

## 📋 Résumé du Système

Votre système de réinitialisation de mot de passe est maintenant **ultra-sécurisé** avec :

- ✅ **Double authentification** : Code OTP + Lien de réinitialisation
- ✅ **Durée de validité** : 5 minutes (sécurité optimale)
- ✅ **Limitation de taux** : Maximum 3 tentatives par email par heure
- ✅ **Nettoyage automatique** : Suppression des anciens tokens
- ✅ **Envoi d'email** : Via SMTP Gmail avec template professionnel

## 🔧 Configurations Obligatoires

### 1. Configuration Gmail SMTP

**Fichier :** `backend/arbitrage_project/settings.py`

```python
# Configuration SMTP Gmail pour l'envoi d'emails
EMAIL_HOST_USER = 'votre-email@gmail.com'  # ← REMPLACER
EMAIL_HOST_PASSWORD = 'votre-mot-de-passe-app'  # ← REMPLACER
DEFAULT_FROM_EMAIL = 'votre-email@gmail.com'  # ← REMPLACER
```

**Étapes pour obtenir le mot de passe d'application Gmail :**

1. **Allez sur** [myaccount.google.com](https://myaccount.google.com)
2. **Sécurité** → **Authentification à 2 facteurs** (activez-la)
3. **Sécurité** → **Mots de passe d'application**
4. **Sélectionnez** "Mail" et générez un mot de passe
5. **Copiez** ce mot de passe dans `EMAIL_HOST_PASSWORD`

### 2. Configuration Frontend

**Fichier :** `backend/arbitrage_project/settings.py`

```python
'FRONTEND_RESET_URL': 'https://votre-domaine.com/reset-password/',  # ← REMPLACER
```

## 🚀 Étapes de Déploiement

### Étape 1 : Vérifier les Migrations

```bash
cd backend
python manage.py makemigrations accounts
python manage.py migrate
```

### Étape 2 : Tester le Système

```bash
python test_otp_password_reset.py
```

### Étape 3 : Configurer le Nettoyage Automatique

**Option A : Cron Job (Recommandé)**

Ajoutez à votre crontab :

```bash
# Nettoyer les tokens toutes les heures
0 * * * * cd /path/to/your/backend && python manage.py cleanup_password_reset_tokens
```

**Option B : Commande Manuelle**

```bash
python manage.py cleanup_password_reset_tokens
```

## 📡 Endpoints API Disponibles

### 1. Demander une Réinitialisation

**POST** `/api/accounts/password-reset/request/`

```json
{
    "email": "utilisateur@example.com"
}
```

**Réponse :**
```json
{
    "success": true,
    "message": "Un email de réinitialisation avec code OTP a été envoyé à utilisateur@example.com",
    "user_type": "arbitre",
    "expires_in_minutes": 5,
    "instructions": "Vérifiez votre email pour le code OTP et le lien de réinitialisation"
}
```

### 2. Vérifier le Code OTP

**POST** `/api/accounts/password-reset/verify-otp/`

```json
{
    "token": "votre-token-de-reinitialisation",
    "otp_code": "123456"
}
```

### 3. Confirmer la Réinitialisation

**POST** `/api/accounts/password-reset/confirm/`

```json
{
    "token": "votre-token-de-reinitialisation",
    "new_password": "nouveauMotDePasse123",
    "confirm_password": "nouveauMotDePasse123"
}
```

### 4. Valider un Token

**GET** `/api/accounts/password-reset/validate/{token}/`

## 🔒 Sécurité Implémentée

### Limitation de Taux
- **Maximum 3 tentatives** par email par heure
- **Code d'erreur 429** si limite dépassée

### Durée de Validité
- **5 minutes** pour les tokens (configurable)
- **Expiration automatique** des codes OTP

### Nettoyage Automatique
- **Suppression automatique** des tokens expirés
- **Nettoyage des anciens tokens** après 1 heure

### Traçabilité
- **Enregistrement de l'IP** et User-Agent
- **Logs complets** des tentatives
- **Historique des utilisations**

## 📧 Template Email

L'email envoyé contient :

- 🔐 **Code OTP** mis en évidence
- 🔗 **Lien de réinitialisation** sécurisé
- ⚠️ **Instructions de sécurité**
- 🎨 **Design professionnel** avec branding

## 🛠️ Maintenance

### Commandes Utiles

```bash
# Nettoyer les tokens (simulation)
python manage.py cleanup_password_reset_tokens --dry-run

# Nettoyer les tokens (exécution)
python manage.py cleanup_password_reset_tokens

# Vérifier les logs
tail -f logs/django.log
```

### Monitoring

Surveillez ces métriques :

- **Taux d'échec** des envois d'email
- **Nombre de tentatives** par heure
- **Tokens expirés** non utilisés
- **Erreurs de validation** OTP

## 🚨 Codes d'Erreur

| Code | Description |
|------|-------------|
| `USER_NOT_FOUND` | Email non trouvé |
| `RATE_LIMIT_EXCEEDED` | Trop de tentatives |
| `INVALID_TOKEN` | Token invalide/expiré |
| `INVALID_OTP` | Code OTP incorrect |
| `OTP_NOT_VERIFIED` | OTP non vérifié |
| `EMAIL_SEND_ERROR` | Erreur envoi email |
| `VALIDATION_ERROR` | Erreur validation |

## ✅ Checklist de Déploiement

- [ ] Configuration Gmail SMTP
- [ ] URL frontend mise à jour
- [ ] Migrations appliquées
- [ ] Tests fonctionnels passés
- [ ] Cron job configuré
- [ ] Monitoring en place
- [ ] Documentation équipe

## 🆘 Support

En cas de problème :

1. **Vérifiez les logs** Django
2. **Testez la configuration** Gmail
3. **Vérifiez les migrations**
4. **Consultez les codes d'erreur**

---

**🎉 Félicitations !** Votre système de réinitialisation de mot de passe est maintenant **ultra-sécurisé** et prêt pour la production !
















