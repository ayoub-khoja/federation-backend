#!/usr/bin/env python3
"""
Script de test pour déboguer le problème de réinitialisation de mot de passe
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
EMAIL = "ayoubramezkhoja2003@gmail.com"

def test_password_reset_flow():
    """Test complet du flux de réinitialisation de mot de passe"""
    
    print("🔍 Test de réinitialisation de mot de passe avec débogage")
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
    
    # Étape 2: Vérifier le code OTP (vous devez le récupérer depuis l'email)
    print("\n2️⃣ Vérification du code OTP...")
    print("⚠️  IMPORTANT: Vérifiez votre email pour le code OTP et le token!")
    print("Entrez le code OTP reçu par email:")
    otp_code = input("Code OTP (6 chiffres): ").strip()
    
    print("Entrez le token reçu par email (partie après ?token=):")
    token = input("Token: ").strip()
    
    # Vérifier l'OTP
    response = requests.post(f"{BASE_URL}/api/accounts/password-reset/verify-otp/", {
        'token': token,
        'otp_code': otp_code
    })
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code != 200:
        print("❌ Échec de la vérification OTP")
        return
    
    # Étape 3: Confirmer la réinitialisation
    print("\n3️⃣ Confirmation de la réinitialisation...")
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
        print(f"🔍 Vérifiez les logs du serveur Django pour voir les messages de débogage")
        print(f"🔍 Nouveau mot de passe: {new_password}")
    else:
        print("❌ Échec de la confirmation")

if __name__ == "__main__":
    test_password_reset_flow()
