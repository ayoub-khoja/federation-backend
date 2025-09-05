#!/usr/bin/env python3
"""
Test simple de connexion
"""

import requests

# Configuration
BASE_URL = "http://localhost:8000"
EMAIL = "ayoubramezkhoja2003@gmail.com"
PASSWORD = "NouveauMotDePasse123!"

def test_simple_login():
    """Test simple de connexion"""
    
    print("🔍 Test simple de connexion")
    print("=" * 40)
    
    try:
        response = requests.post(f"{BASE_URL}/api/accounts/login/", {
            'email': EMAIL,
            'password': PASSWORD
        })
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Connexion réussie!")
        else:
            print("❌ Échec de la connexion")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_simple_login()








