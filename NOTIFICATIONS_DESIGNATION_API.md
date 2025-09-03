# 🏆 API Notifications de Désignation d'Arbitres

## 📋 Vue d'ensemble

Le système de notifications de désignation permet aux administrateurs de notifier automatiquement les arbitres lorsqu'ils sont désignés pour un match. Le système utilise Firebase Cloud Messaging (FCM) pour envoyer des notifications push en temps réel.

## 🔧 Fonctionnalités

- ✅ **Notification individuelle** : Notifier un arbitre spécifique
- ✅ **Notification multiple** : Notifier plusieurs arbitres en une fois
- ✅ **Historique complet** : Suivi de toutes les notifications
- ✅ **Marquage comme lu** : Gestion du statut de lecture
- ✅ **Intégration FCM** : Notifications push en temps réel
- ✅ **Gestion d'erreurs** : Suivi des échecs d'envoi
- ✅ **Pagination** : Gestion des grandes listes
- ✅ **Filtres** : Par statut, date, etc.

## 📱 Types de Désignation

| Type | Description |
|------|-------------|
| `arbitre_principal` | Arbitre Principal |
| `arbitre_assistant_1` | Assistant 1 |
| `arbitre_assistant_2` | Assistant 2 |
| `arbitre_quatrieme` | Quatrième Arbitre |
| `commissaire_match` | Commissaire de Match |

## 📊 Statuts des Notifications

| Statut | Description |
|--------|-------------|
| `sent` | Envoyée |
| `delivered` | Livrée |
| `read` | Lue |
| `failed` | Échouée |

## 🔗 Endpoints API

### 1. Notifier un Arbitre

**POST** `/api/accounts/arbitres/notify-designation/`

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Body:**
```json
{
  "arbitre_id": 123,
  "arbitre_nom": "Jean Dupont",
  "arbitre_email": "jean.dupont@email.com",
  "match_id": 456,
  "match_nom": "Match de championnat",
  "match_date": "2024-01-15T14:00:00Z",
  "match_lieu": "Stade Municipal",
  "designation_type": "arbitre_principal",
  "message": "Vous avez été désigné comme arbitre principal"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Notification de désignation envoyée",
  "notification_id": 789,
  "arbitre": {
    "id": 123,
    "nom": "Jean Dupont",
    "email": "jean.dupont@email.com"
  },
  "fcm_results": {
    "success_count": 1,
    "errors": 0,
    "details": [...]
  }
}
```

### 2. Notifier Plusieurs Arbitres

**POST** `/api/accounts/arbitres/notify-multiple/`

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Body:**
```json
{
  "notifications": [
    {
      "arbitre_id": 123,
      "arbitre_nom": "Jean Dupont",
      "arbitre_email": "jean.dupont@email.com",
      "match_id": 456,
      "match_nom": "Match de championnat",
      "match_date": "2024-01-15T14:00:00Z",
      "match_lieu": "Stade Municipal",
      "designation_type": "arbitre_principal",
      "message": "Vous avez été désigné comme arbitre principal"
    },
    {
      "arbitre_id": 124,
      "arbitre_nom": "Marie Martin",
      "arbitre_email": "marie.martin@email.com",
      "match_id": 456,
      "match_nom": "Match de championnat",
      "match_date": "2024-01-15T14:00:00Z",
      "match_lieu": "Stade Municipal",
      "designation_type": "arbitre_assistant_1",
      "message": "Vous avez été désigné comme assistant 1"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Notifications envoyées: 2 succès, 0 erreurs",
  "summary": {
    "total": 2,
    "success_count": 2,
    "error_count": 0
  },
  "results": [
    {
      "arbitre_id": 123,
      "arbitre_nom": "Jean Dupont",
      "notification_id": 789,
      "success": true,
      "fcm_results": {...}
    },
    {
      "arbitre_id": 124,
      "arbitre_nom": "Marie Martin",
      "notification_id": 790,
      "success": true,
      "fcm_results": {...}
    }
  ]
}
```

### 3. Historique des Notifications

**GET** `/api/accounts/arbitres/{arbitre_id}/notifications/`

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**
- `page` (optional): Numéro de page (défaut: 1)
- `page_size` (optional): Taille de page (défaut: 20)
- `status` (optional): Filtrer par statut (`sent`, `delivered`, `read`, `failed`)

**Response:**
```json
{
  "success": true,
  "arbitre": {
    "id": 123,
    "nom": "Jean Dupont",
    "email": "jean.dupont@email.com"
  },
  "notifications": [
    {
      "id": 789,
      "match_id": 456,
      "match_nom": "Match de championnat",
      "match_date": "2024-01-15T14:00:00Z",
      "match_lieu": "Stade Municipal",
      "designation_type": "arbitre_principal",
      "designation_type_display": "Arbitre Principal",
      "title": "🏆 Nouvelle Désignation - Match de championnat",
      "message": "Vous avez été désigné comme arbitre principal",
      "status": "delivered",
      "status_display": "Livrée",
      "is_read": false,
      "created_at": "2024-01-10T10:00:00Z",
      "sent_at": "2024-01-10T10:00:05Z",
      "read_at": null,
      "is_recent": true
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 1,
    "total_count": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

### 4. Marquer une Notification comme Lue

**POST** `/api/accounts/notifications/{notification_id}/read/`

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Notification marquée comme lue",
  "notification_id": 789,
  "read_at": "2024-01-10T15:30:00Z"
}
```

## 🔐 Authentification

Tous les endpoints nécessitent une authentification JWT valide :

```bash
# Pour les administrateurs (notifications)
Authorization: Bearer <admin_jwt_token>

# Pour les arbitres (consultation de leurs notifications)
Authorization: Bearer <arbitre_jwt_token>
```

## 📱 Intégration Frontend

### Exemple d'utilisation avec JavaScript

```javascript
// Notifier un arbitre
const notifyArbitre = async (arbitreData) => {
  const response = await fetch('/api/accounts/arbitres/notify-designation/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${adminToken}`
    },
    body: JSON.stringify(arbitreData)
  });
  
  return response.json();
};

// Notifier plusieurs arbitres
const notifyMultipleArbitres = async (notificationsData) => {
  const response = await fetch('/api/accounts/arbitres/notify-multiple/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${adminToken}`
    },
    body: JSON.stringify(notificationsData)
  });
  
  return response.json();
};

// Récupérer l'historique des notifications
const getNotificationsHistory = async (arbitreId, page = 1) => {
  const response = await fetch(`/api/accounts/arbitres/${arbitreId}/notifications/?page=${page}`, {
    headers: {
      'Authorization': `Bearer ${arbitreToken}`
    }
  });
  
  return response.json();
};

// Marquer une notification comme lue
const markNotificationRead = async (notificationId) => {
  const response = await fetch(`/api/accounts/notifications/${notificationId}/read/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${arbitreToken}`
    }
  });
  
  return response.json();
};
```

## 🚨 Gestion des Erreurs

### Codes d'erreur HTTP

| Code | Description |
|------|-------------|
| 400 | Données invalides ou champs manquants |
| 401 | Token d'authentification manquant ou invalide |
| 403 | Accès refusé (permissions insuffisantes) |
| 404 | Arbitre ou notification non trouvé |
| 500 | Erreur interne du serveur |

### Exemple de réponse d'erreur

```json
{
  "error": "Champ requis manquant: arbitre_id",
  "success": false
}
```

## 📊 Monitoring et Statistiques

Le système enregistre automatiquement :
- ✅ **Statut d'envoi** : Succès/échec de chaque notification
- ✅ **Réponse FCM** : Détails de la réponse Firebase
- ✅ **Timestamps** : Dates de création, envoi, lecture
- ✅ **Erreurs** : Messages d'erreur détaillés

## 🔄 Workflow Complet

1. **Admin crée une désignation** → Frontend appelle l'API
2. **Backend enregistre la notification** → Base de données
3. **Envoi FCM automatique** → Firebase Cloud Messaging
4. **Arbitre reçoit la notification** → Application mobile
5. **Arbitre consulte l'historique** → API de consultation
6. **Marquage comme lu** → Mise à jour du statut

## 🚀 Déploiement

Le système est prêt pour la production avec :
- ✅ **Migrations appliquées** : Base de données mise à jour
- ✅ **Tests validés** : Fonctionnalités testées
- ✅ **Documentation complète** : Guide d'utilisation
- ✅ **Gestion d'erreurs** : Robustesse assurée

## 📞 Support

Pour toute question ou problème :
- 📧 Email : support@federation-arbitrage.com
- 📱 Téléphone : +216 XX XXX XXX
- 🌐 Documentation : [Lien vers la documentation complète]



