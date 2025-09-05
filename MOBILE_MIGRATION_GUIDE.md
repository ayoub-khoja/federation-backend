# 📱 Guide de Migration vers Firebase Cloud Messaging (FCM)

## 🎯 Vue d'ensemble

Ce guide vous explique comment migrer vos applications mobiles iOS et Android de l'ancien système de notifications push vers Firebase Cloud Messaging (FCM).

## 🔧 **Étape 1 : Configuration Firebase Console**

### 1.1 Créer un projet Firebase
1. Allez sur [Firebase Console](https://console.firebase.google.com/)
2. Cliquez sur "Créer un projet"
3. Nommez votre projet : `federation-arbitrage`
4. Activez Google Analytics (optionnel)

### 1.2 Ajouter les applications
1. **iOS** : Cliquez sur "Ajouter une application" → iOS
   - Bundle ID : `com.company.federation`
   - Nom de l'app : `Federation Arbitrage iOS`
   
2. **Android** : Cliquez sur "Ajouter une application" → Android
   - Package name : `android.federation`
   - Nom de l'app : `Federation Arbitrage Android`

### 1.3 Télécharger les fichiers de configuration
- **iOS** : Téléchargez `GoogleService-Info.plist`
- **Android** : Téléchargez `google-services.json`

### 1.4 Générer la clé de service
1. Allez dans "Paramètres du projet" → "Comptes de service"
2. Cliquez sur "Générer une nouvelle clé privée"
3. Téléchargez le fichier JSON
4. Renommez-le en `firebase-service-account-key.json`
5. Placez-le dans le dossier `backend/`

## 📱 **Étape 2 : Migration iOS (Swift)**

### 2.1 Installation des dépendances
```bash
# Dans votre projet iOS
pod init
```

Ajoutez dans `Podfile` :
```ruby
platform :ios, '12.0'
use_frameworks!

target 'FederationArbitrage' do
  pod 'Firebase/Core'
  pod 'Firebase/Messaging'
  pod 'Firebase/Analytics'
end
```

```bash
pod install
```

### 2.2 Configuration AppDelegate
```swift
// AppDelegate.swift
import UIKit
import Firebase
import UserNotifications

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        
        // Configuration Firebase
        FirebaseApp.configure()
        
        // Configuration des notifications
        UNUserNotificationCenter.current().delegate = self
        
        // Demander la permission pour les notifications
        let authOptions: UNAuthorizationOptions = [.alert, .badge, .sound]
        UNUserNotificationCenter.current().requestAuthorization(
            options: authOptions,
            completionHandler: { granted, error in
                if granted {
                    DispatchQueue.main.async {
                        application.registerForRemoteNotifications()
                    }
                }
            }
        )
        
        // Configuration FCM
        Messaging.messaging().delegate = self
        
        return true
    }
    
    // Enregistrement pour les notifications push
    func application(_ application: UIApplication, didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
        Messaging.messaging().apnsToken = deviceToken
    }
}

// Extension pour FCM
extension AppDelegate: MessagingDelegate {
    func messaging(_ messaging: Messaging, didReceiveRegistrationToken fcmToken: String?) {
        print("Firebase registration token: \(String(describing: fcmToken))")
        
        // Envoyer le token au backend Django
        if let token = fcmToken {
            sendFCMTokenToBackend(token: token, deviceType: "ios")
        }
    }
}

// Extension pour les notifications
extension AppDelegate: UNUserNotificationCenterDelegate {
    // Notification reçue en foreground
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                              willPresent notification: UNNotification,
                              withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        let userInfo = notification.request.content.userInfo
        
        // Traiter les données de la notification
        if let matchId = userInfo["match_id"] as? String {
            // Naviguer vers la page du match
            handleMatchNotification(matchId: matchId)
        }
        
        // Afficher la notification même en foreground
        completionHandler([.alert, .badge, .sound])
    }
    
    // Notification tapée par l'utilisateur
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                              didReceive response: UNNotificationResponse,
                              withCompletionHandler completionHandler: @escaping () -> Void) {
        let userInfo = response.notification.request.content.userInfo
        
        // Traiter l'action de l'utilisateur
        if let matchId = userInfo["match_id"] as? String {
            handleMatchNotification(matchId: matchId)
        }
        
        completionHandler()
    }
}

// Fonction pour envoyer le token FCM au backend
func sendFCMTokenToBackend(token: String, deviceType: String) {
    guard let url = URL(string: "https://federation-backend.onrender.com/api/accounts/fcm/subscribe/") else {
        return
    }
    
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    // Ajouter le token JWT d'authentification
    if let jwtToken = UserDefaults.standard.string(forKey: "jwt_token") {
        request.setValue("Bearer \(jwtToken)", forHTTPHeaderField: "Authorization")
    }
    
    let body: [String: Any] = [
        "fcm_token": token,
        "device_type": deviceType,
        "device_id": UIDevice.current.identifierForVendor?.uuidString ?? "",
        "app_version": Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0.0"
    ]
    
    do {
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
    } catch {
        print("Erreur lors de la sérialisation JSON: \(error)")
        return
    }
    
    URLSession.shared.dataTask(with: request) { data, response, error in
        if let error = error {
            print("Erreur lors de l'envoi du token FCM: \(error)")
            return
        }
        
        if let httpResponse = response as? HTTPURLResponse {
            print("Token FCM envoyé avec succès. Status: \(httpResponse.statusCode)")
        }
    }.resume()
}

// Fonction pour gérer les notifications de match
func handleMatchNotification(matchId: String) {
    // Naviguer vers la page du match
    DispatchQueue.main.async {
        // Implémentation de la navigation
        // Par exemple, utiliser un NotificationCenter ou un Router
        NotificationCenter.default.post(
            name: NSNotification.Name("NavigateToMatch"),
            object: nil,
            userInfo: ["match_id": matchId]
        )
    }
}
```

### 2.3 Configuration des capacités
Dans Xcode :
1. Sélectionnez votre projet
2. Allez dans "Signing & Capabilities"
3. Ajoutez "Push Notifications"
4. Ajoutez "Background Modes" → "Background processing"

## 🤖 **Étape 3 : Migration Android (Kotlin)**

### 3.1 Configuration Gradle
```gradle
// build.gradle (Project level)
buildscript {
    dependencies {
        classpath 'com.google.gms:google-services:4.3.15'
    }
}

// build.gradle (Module level)
apply plugin: 'com.google.gms.google-services'

dependencies {
    implementation platform('com.google.firebase:firebase-bom:32.7.0')
    implementation 'com.google.firebase:firebase-messaging'
    implementation 'com.google.firebase:firebase-analytics'
    implementation 'com.google.firebase:firebase-core'
}
```

### 3.2 Service de messagerie FCM
```kotlin
// FCMService.kt
package com.federation.arbitrage

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage

class FCMService : FirebaseMessagingService() {
    
    override fun onNewToken(token: String) {
        super.onNewToken(token)
        println("Firebase registration token: $token")
        
        // Envoyer le token au backend Django
        sendFCMTokenToBackend(token, "android")
    }
    
    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        super.onMessageReceived(remoteMessage)
        
        // Traiter les données de la notification
        val data = remoteMessage.data
        val matchId = data["match_id"]
        
        if (matchId != null) {
            handleMatchNotification(matchId)
        }
        
        // Afficher la notification
        showNotification(
            title = remoteMessage.notification?.title ?: "Nouvelle notification",
            body = remoteMessage.notification?.body ?: "",
            data = data
        )
    }
    
    private fun sendFCMTokenToBackend(token: String, deviceType: String) {
        val url = "https://federation-backend.onrender.com/api/accounts/fcm/subscribe/"
        
        // Utiliser votre client HTTP préféré (Retrofit, OkHttp, etc.)
        // Exemple avec une coroutine
        lifecycleScope.launch {
            try {
                val response = httpClient.post(url) {
                    headers {
                        append("Content-Type", "application/json")
                        // Ajouter le token JWT d'authentification
                        val jwtToken = getStoredJwtToken()
                        if (jwtToken != null) {
                            append("Authorization", "Bearer $jwtToken")
                        }
                    }
                    setBody(
                        """
                        {
                            "fcm_token": "$token",
                            "device_type": "$deviceType",
                            "device_id": "${getDeviceId()}",
                            "app_version": "${getAppVersion()}"
                        }
                        """.trimIndent()
                    )
                }
                
                if (response.status.isSuccess()) {
                    println("Token FCM envoyé avec succès")
                }
            } catch (e: Exception) {
                println("Erreur lors de l'envoi du token FCM: ${e.message}")
            }
        }
    }
    
    private fun showNotification(title: String, body: String, data: Map<String, String>) {
        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        
        // Créer le canal de notification (Android 8.0+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                "federation_channel",
                "Federation Arbitrage",
                NotificationManager.IMPORTANCE_HIGH
            )
            notificationManager.createNotificationChannel(channel)
        }
        
        // Créer l'intent pour ouvrir l'app
        val intent = Intent(this, MainActivity::class.java)
        intent.putExtra("match_id", data["match_id"])
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        // Construire la notification
        val notification = NotificationCompat.Builder(this, "federation_channel")
            .setContentTitle(title)
            .setContentText(body)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .build()
        
        // Afficher la notification
        notificationManager.notify(System.currentTimeMillis().toInt(), notification)
    }
    
    private fun handleMatchNotification(matchId: String) {
        // Naviguer vers la page du match
        val intent = Intent(this, MatchDetailActivity::class.java)
        intent.putExtra("match_id", matchId)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
        startActivity(intent)
    }
    
    private fun getDeviceId(): String {
        return Settings.Secure.getString(contentResolver, Settings.Secure.ANDROID_ID)
    }
    
    private fun getAppVersion(): String {
        return try {
            val packageInfo = packageManager.getPackageInfo(packageName, 0)
            packageInfo.versionName
        } catch (e: Exception) {
            "1.0.0"
        }
    }
    
    private fun getStoredJwtToken(): String? {
        val sharedPref = getSharedPreferences("auth_prefs", Context.MODE_PRIVATE)
        return sharedPref.getString("jwt_token", null)
    }
}
```

### 3.3 Configuration du manifeste
```xml
<!-- AndroidManifest.xml -->
<application>
    <!-- Service FCM -->
    <service
        android:name=".FCMService"
        android:exported="false">
        <intent-filter>
            <action android:name="com.google.firebase.MESSAGING_EVENT" />
        </intent-filter>
    </service>
    
    <!-- Métadonnées Firebase -->
    <meta-data
        android:name="com.google.firebase.messaging.default_notification_icon"
        android:resource="@drawable/ic_notification" />
    <meta-data
        android:name="com.google.firebase.messaging.default_notification_color"
        android:resource="@color/notification_color" />
    <meta-data
        android:name="com.google.firebase.messaging.default_notification_channel_id"
        android:value="federation_channel" />
</application>

<!-- Permissions -->
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.WAKE_LOCK" />
<uses-permission android:name="android.permission.VIBRATE" />
```

## 🧪 **Étape 4 : Tests**

### 4.1 Test depuis le backend
```python
# Test d'envoi de notification
from accounts.firebase_config import send_notification_to_user

# Récupérer un utilisateur avec un token FCM
arbitre = Arbitre.objects.filter(fcm_tokens__is_active=True).first()

if arbitre:
    results = send_notification_to_user(
        user=arbitre,
        title="🧪 Test FCM",
        body="Ceci est un test de notification FCM",
        data={'type': 'test', 'timestamp': '2025-01-02T15:30:00Z'}
    )
    print(f"Résultats: {results}")
```

### 4.2 Test depuis l'API
```bash
# Test d'enregistrement de token
curl -X POST https://federation-backend.onrender.com/api/accounts/fcm/subscribe/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "fcm_token": "test_token_123",
    "device_type": "android",
    "device_id": "device_123",
    "app_version": "1.0.0"
  }'

# Test d'envoi de notification
curl -X POST https://federation-backend.onrender.com/api/accounts/fcm/test/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔄 **Étape 5 : Migration Progressive**

### 5.1 Phase 1 : Déploiement parallèle
- Garder l'ancien système actif
- Déployer FCM en parallèle
- Tester avec un petit groupe d'utilisateurs

### 5.2 Phase 2 : Migration des utilisateurs
- Notifier les utilisateurs de la mise à jour
- Inciter à mettre à jour l'application
- Surveiller les métriques d'adoption

### 5.3 Phase 3 : Désactivation de l'ancien système
- Une fois que 90%+ des utilisateurs ont migré
- Désactiver progressivement l'ancien système
- Nettoyer le code legacy

## 📊 **Étape 6 : Monitoring et Analytics**

### 6.1 Métriques à surveiller
- Taux d'adoption FCM
- Taux de livraison des notifications
- Taux d'erreur par plateforme
- Temps de réponse des notifications

### 6.2 Dashboard de monitoring
```python
# Créer un endpoint de monitoring
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def fcm_monitoring_dashboard(request):
    stats = get_notification_stats()
    return Response({
        'fcm_adoption_rate': calculate_adoption_rate(),
        'delivery_rate': calculate_delivery_rate(),
        'error_rate': calculate_error_rate(),
        'platform_distribution': stats['by_platform']
    })
```

## ✅ **Checklist de Migration**

- [ ] Firebase Admin SDK installé
- [ ] Configuration Firebase ajoutée dans settings.py
- [ ] Fichier de clé de service téléchargé
- [ ] Application iOS configurée avec FCM
- [ ] Application Android configurée avec FCM
- [ ] Tests d'envoi de notifications réussis
- [ ] Monitoring en place
- [ ] Documentation mise à jour
- [ ] Équipe formée sur FCM
- [ ] Plan de rollback préparé

## 🚨 **Points d'attention**

1. **Sécurité** : Ne jamais commiter les clés Firebase
2. **Performance** : Surveiller l'impact sur les performances
3. **Compatibilité** : Tester sur différentes versions d'OS
4. **Fallback** : Garder l'ancien système en backup
5. **Monitoring** : Surveiller les logs d'erreur

---

🎉 **Une fois la migration terminée, vous bénéficierez d'un système de notifications plus fiable, plus rapide et plus facile à maintenir !**











