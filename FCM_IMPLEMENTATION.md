# 🔥 Firebase Cloud Messaging (FCM) - Implémentation

## 📋 Vue d'ensemble

Le système Firebase Cloud Messaging (FCM) a été implémenté pour remplacer l'ancien système de notifications push. Il permet d'envoyer des notifications sur iOS, Android et Web de manière unifiée.

## 🏗️ Architecture

### Modèles
- **FCMToken** : Stocke les tokens FCM des appareils mobiles
  - Support pour iOS, Android et Web
  - Association avec Arbitre, Commissaire ou Admin
  - Gestion des métadonnées (device_id, app_version, etc.)

### Configuration
- **firebase_config.py** : Configuration et fonctions de notification
  - Initialisation Firebase Admin SDK
  - Envoi de notifications par plateforme
  - Gestion des erreurs et logging

### API Endpoints
- `POST /api/accounts/fcm/subscribe/` : Enregistrer un token FCM
- `POST /api/accounts/fcm/unsubscribe/` : Désactiver un token FCM
- `GET /api/accounts/fcm/status/` : Statut des tokens de l'utilisateur
- `POST /api/accounts/fcm/test/` : Tester l'envoi de notification
- `GET /api/accounts/fcm/stats/` : Statistiques (admin seulement)
- `POST /api/accounts/fcm/broadcast/` : Envoyer un broadcast (admin seulement)

## 🚀 Utilisation

### 1. Enregistrement d'un token FCM (Mobile)

```javascript
// Exemple pour une app mobile
const registerFCMToken = async (fcmToken, deviceType) => {
  const response = await fetch('/api/accounts/fcm/subscribe/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${jwtToken}`
    },
    body: JSON.stringify({
      fcm_token: fcmToken,
      device_type: deviceType, // 'ios', 'android', ou 'web'
      device_id: 'unique_device_id',
      app_version: '1.0.0'
    })
  });
  
  return response.json();
};
```

### 2. Envoi de notification depuis le backend

```python
from accounts.firebase_config import send_notification_to_user

# Envoyer à un utilisateur spécifique
results = send_notification_to_user(
    user=arbitre,
    title="Nouvelle désignation",
    body="Vous avez été désigné pour arbitrer un match",
    data={'match_id': '123', 'type': 'designation'}
)

# Envoyer à tous les utilisateurs
from accounts.firebase_config import send_notification_to_all_platforms

results = send_notification_to_all_platforms(
    title="Maintenance programmée",
    body="L'application sera en maintenance demain",
    data={'type': 'maintenance'}
)
```

### 3. Configuration Firebase

Pour activer les notifications réelles, ajoutez dans `settings.py` :

```python
# Configuration Firebase
FIREBASE_SERVICE_ACCOUNT_PATH = 'path/to/firebase-service-account-key.json'
# OU
FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": "your-project-id",
    # ... autres clés Firebase
}
```

## 📱 Intégration Mobile

### iOS (Swift)
```swift
import Firebase
import UserNotifications

// Dans AppDelegate
func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    FirebaseApp.configure()
    
    // Demander permission
    UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
        if granted {
            DispatchQueue.main.async {
                application.registerForRemoteNotifications()
            }
        }
    }
    
    return true
}

// Obtenir le token FCM
Messaging.messaging().token { token, error in
    if let token = token {
        // Envoyer le token au backend
        sendTokenToBackend(token: token, deviceType: "ios")
    }
}
```

### Android (Kotlin)
```kotlin
import com.google.firebase.messaging.FirebaseMessaging

// Obtenir le token FCM
FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
    if (!task.isSuccessful) {
        return@addOnCompleteListener
    }
    
    val token = task.result
    // Envoyer le token au backend
    sendTokenToBackend(token, "android")
}
```

## 🔧 Installation Firebase Admin SDK

Pour activer les notifications réelles, installez le SDK Firebase :

```bash
pip install firebase-admin
```

## 📊 Statistiques et Monitoring

### Obtenir les statistiques
```python
from accounts.firebase_config import get_notification_stats

stats = get_notification_stats()
print(f"Total tokens: {stats['total_tokens']}")
print(f"Tokens actifs: {stats['active_tokens']}")
print(f"Par plateforme: {stats['by_platform']}")
```

### Nettoyage des tokens inactifs
```python
from accounts.firebase_config import cleanup_inactive_tokens

count = cleanup_inactive_tokens()
print(f"{count} tokens marqués comme inactifs")
```

## 🛡️ Sécurité

- Tous les endpoints FCM nécessitent une authentification JWT
- Les tokens FCM sont uniques et associés à un utilisateur
- Validation des types d'appareils (ios, android, web)
- Gestion des erreurs et logging complet

## 🔄 Migration depuis l'ancien système

L'ancien système de notifications push (PushSubscription) reste disponible pour la compatibilité, mais il est recommandé de migrer vers FCM pour :

- Meilleure fiabilité
- Support multi-plateforme
- Gestion centralisée
- Statistiques avancées

## 📝 Notes importantes

1. **Firebase Admin SDK** : Nécessaire pour l'envoi réel de notifications
2. **Configuration** : Ajoutez vos clés Firebase dans les settings
3. **Test** : Utilisez l'endpoint `/fcm/test/` pour tester les notifications
4. **Monitoring** : Surveillez les logs pour détecter les erreurs d'envoi
5. **Nettoyage** : Exécutez régulièrement `cleanup_inactive_tokens()`

## 🎯 Prochaines étapes

1. Installer Firebase Admin SDK
2. Configurer les clés Firebase
3. Tester avec des appareils réels
4. Migrer les applications mobiles vers FCM
5. Déployer en production

---

✅ **Système FCM implémenté avec succès !**

