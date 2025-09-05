#!/usr/bin/env python3
"""
Test final de toutes les APIs de compétitions
"""
import requests
import time

def test_api(endpoint, name):
    """Test d'une API"""
    try:
        response = requests.get(f'http://localhost:8000/api/matches/{endpoint}/', timeout=3)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name}: {data.get('message')}")
        elif response.status_code == 404:
            print(f"⚠️ {name}: Type non configuré en base")
        else:
            print(f"❌ {name}: Erreur {response.status_code}")
    except Exception as e:
        print(f"❌ {name}: Connexion échouée")

def main():
    print("🏆 Test des APIs de compétitions")
    print("=" * 50)
    
    # Attendre que le serveur démarre
    time.sleep(2)
    
    competitions = [
        ('ligue1', 'Ligue 1'),
        ('ligue2', 'Ligue 2'), 
        ('c1', 'C1'),
        ('c2', 'C2'),
        ('jeunes', 'Jeunes'),
        ('coupe-tunisie', 'Coupe de Tunisie')
    ]
    
    for endpoint, name in competitions:
        test_api(endpoint, name)
    
    print("\n📋 URLs disponibles:")
    for endpoint, name in competitions:
        print(f"   GET /api/matches/{endpoint}/")

if __name__ == '__main__':
    main()






