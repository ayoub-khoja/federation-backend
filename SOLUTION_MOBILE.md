# 🚨 SOLUTION IMMÉDIATE - Problème de connexion mobile

## Le problème
Le pare-feu Windows bloque l'accès au port 8000 depuis votre téléphone.

## ✅ SOLUTION RAPIDE (2 minutes)

### Option 1 : Désactiver temporairement le pare-feu
1. **Ouvrez le Pare-feu Windows Defender**
2. **Cliquez sur "Activer ou désactiver le Pare-feu Windows Defender"**
3. **Désactivez temporairement le pare-feu pour les réseaux privés**
4. **Testez la connexion sur votre téléphone**
5. **Réactivez le pare-feu après le test**

### Option 2 : Ouvrir le port manuellement
1. **Ouvrez le Pare-feu Windows Defender**
2. **Cliquez sur "Paramètres avancés"**
3. **Cliquez sur "Règles de trafic entrant"**
4. **Cliquez sur "Nouvelle règle..."**
5. **Sélectionnez "Port"**
6. **Choisissez "TCP" et entrez "8000"**
7. **Sélectionnez "Autoriser la connexion"**
8. **Cochez tous les profils**
9. **Nommez la règle "Django Server"**

### Option 3 : Utiliser un autre port
```bash
python manage.py runserver 0.0.0.0:8080
```
Puis testez : `http://192.168.1.100:8080`

## 📱 Test de connexion
1. **Ouvrez le navigateur de votre téléphone**
2. **Tapez :** `http://192.168.1.100:8000`
3. **Si ça marche, l'application devrait fonctionner**

## 🔧 Si ça ne marche toujours pas
1. **Redémarrez le routeur WiFi**
2. **Vérifiez que le téléphone et l'ordinateur sont sur le même WiFi**
3. **Essayez de partager la connexion mobile de votre téléphone**

## ✅ Le serveur fonctionne déjà !
Le serveur Django est démarré et accessible localement. Le seul problème est le pare-feu Windows.


