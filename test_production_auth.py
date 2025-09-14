#!/usr/bin/env python3
"""
Test d'authentification en production
"""
import requests
import json

def test_production_auth():
    """Tester l'authentification en production"""
    
    print("🧪 TEST D'AUTHENTIFICATION EN PRODUCTION")
    print("=" * 50)
    
    base_url = "https://federation-backend.onrender.com"
    
    # Test 1: Login pour obtenir un token
    print("\n1️⃣ Test de login...")
    login_data = {
        "phone_number": "+21699957980",  # Remplacez par un numéro valide
        "password": "votre_mot_de_passe"  # Remplacez par le mot de passe
    }
    
    try:
        response = requests.post(f"{base_url}/api/accounts/auth/login/", json=login_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"   ✅ Token obtenu: {token[:50]}...")
            
            # Test 2: Utiliser le token pour accéder aux excuses
            print("\n2️⃣ Test d'accès aux excuses...")
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{base_url}/api/accounts/arbitres/excuses/", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Succès: {data.get('message')}")
                print(f"   📊 Nombre d'excuses: {len(data.get('excuses', []))}")
            else:
                print(f"   ❌ Erreur: {response.text}")
                
        else:
            print(f"   ❌ Erreur de login: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    test_production_auth()

