#!/usr/bin/env python3
"""
Test de connexion avec le nouveau mot de passe
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
EMAIL = "ayoubramezkhoja2003@gmail.com"
NEW_PASSWORD = "NouveauMotDePasse123!"

def test_login():
    """Test de connexion avec le nouveau mot de passe"""
    
    print("🔍 Test de connexion avec le nouveau mot de passe")
    print("=" * 60)
    
    # Test de connexion
    print(f"\n1️⃣ Tentative de connexion avec:")
    print(f"   Email: {EMAIL}")
    print(f"   Mot de passe: {NEW_PASSWORD}")
    
    response = requests.post(f"{BASE_URL}/api/accounts/login/", {
        'email': EMAIL,
        'password': NEW_PASSWORD
    })
    
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("✅ Connexion réussie avec le nouveau mot de passe!")
        data = response.json()
        if 'access' in data:
            print(f"🔑 Token d'accès reçu: {data['access'][:50]}...")
    else:
        print("❌ Échec de la connexion avec le nouveau mot de passe")
        
        # Test avec l'ancien mot de passe pour comparaison
        print(f"\n2️⃣ Test avec l'ancien mot de passe (pour comparaison)...")
        old_response = requests.post(f"{BASE_URL}/api/accounts/login/", {
            'email': EMAIL,
            'password': "ancien_mot_de_passe"  # Remplacez par votre ancien mot de passe
        })
        
        print(f"Status: {old_response.status_code}")
        print(f"Response: {old_response.json()}")

if __name__ == "__main__":
    test_login()






