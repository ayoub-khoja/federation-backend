#!/usr/bin/env python3
"""
Test automatique pour déboguer le problème de réinitialisation de mot de passe
Ce script simule tout le processus sans interaction utilisateur
"""

import requests
import json
import time
from accounts.models import PasswordResetToken, Arbitre

# Configuration
BASE_URL = "http://localhost:8000"
EMAIL = "ayoubramezkhoja2003@gmail.com"

def test_password_reset_automatic():
    """Test automatique complet du flux de réinitialisation de mot de passe"""
    
    print("🔍 Test automatique de réinitialisation de mot de passe")
    print("=" * 60)
    
    # Étape 1: Demander la réinitialisation
    print("\n1️⃣ Demande de réinitialisation...")
    response = requests.post(f"{BASE_URL}/api/accounts/password-reset/request/", {
        'email': EMAIL
    })
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code != 200:
        print("❌ Échec de la demande de réinitialisation")
        return
    
    # Étape 2: Récupérer le token et OTP depuis la base de données
    print("\n2️⃣ Récupération du token et OTP depuis la base de données...")
    
    # Trouver le token le plus récent pour cet email
    try:
        latest_token = PasswordResetToken.objects.filter(
            email=EMAIL,
            is_used=False
        ).order_by('-created_at').first()
        
        if not latest_token:
            print("❌ Aucun token trouvé dans la base de données")
            return
        
        token = latest_token.token
        otp_code = latest_token.otp_code
        
        print(f"✅ Token trouvé: {token[:20]}...")
        print(f"✅ Code OTP: {otp_code}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération du token: {e}")
        return
    
    # Étape 3: Vérifier l'OTP
    print("\n3️⃣ Vérification du code OTP...")
    response = requests.post(f"{BASE_URL}/api/accounts/password-reset/verify-otp/", {
        'token': token,
        'otp_code': otp_code
    })
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code != 200:
        print("❌ Échec de la vérification OTP")
        return
    
    # Étape 4: Confirmer la réinitialisation
    print("\n4️⃣ Confirmation de la réinitialisation...")
    new_password = "NouveauMotDePasse123!"
    
    response = requests.post(f"{BASE_URL}/api/accounts/password-reset/confirm/", {
        'token': token,
        'new_password': new_password,
        'confirm_password': new_password
    })
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Réinitialisation réussie!")
        print(f"🔍 Nouveau mot de passe: {new_password}")
        
        # Étape 5: Vérifier que le mot de passe a vraiment changé
        print("\n5️⃣ Vérification du changement de mot de passe...")
        
        try:
            # Récupérer l'utilisateur depuis la base de données
            user = Arbitre.objects.get(email=EMAIL)
            print(f"🔍 Utilisateur trouvé: {user.first_name} {user.last_name}")
            print(f"🔍 Mot de passe actuel (hash): {user.password}")
            
            # Tester la connexion avec l'ancien mot de passe
            print("\n🔍 Test avec l'ancien mot de passe...")
            old_password_test = user.check_password("ancien_mot_de_passe")  # Remplacez par l'ancien mot de passe
            print(f"🔍 Ancien mot de passe valide: {old_password_test}")
            
            # Tester la connexion avec le nouveau mot de passe
            print("\n🔍 Test avec le nouveau mot de passe...")
            new_password_test = user.check_password(new_password)
            print(f"🔍 Nouveau mot de passe valide: {new_password_test}")
            
            if new_password_test:
                print("✅ Le mot de passe a été correctement changé!")
            else:
                print("❌ Le mot de passe n'a PAS été changé!")
                
        except Exception as e:
            print(f"❌ Erreur lors de la vérification: {e}")
    else:
        print("❌ Échec de la confirmation")

if __name__ == "__main__":
    test_password_reset_automatic()








