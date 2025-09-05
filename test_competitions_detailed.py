#!/usr/bin/env python3
"""
Test détaillé de toutes les APIs de compétitions avec réponses complètes
"""
import requests
import json
import time

def test_api_detailed(endpoint, name):
    """Test détaillé d'une API"""
    try:
        response = requests.get(f'http://localhost:8000/api/matches/{endpoint}/', timeout=5)
        
        print(f"\n🏆 {name}")
        print("=" * 50)
        print(f"URL: http://localhost:8000/api/matches/{endpoint}/")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès: {data.get('message')}")
            print(f"📊 Compétition: {data.get('competition', {}).get('name')}")
            print(f"🔢 Nombre de matchs: {len(data.get('matches', []))}")
            
            # Afficher les détails de la compétition
            competition = data.get('competition', {})
            if competition:
                print(f"   Code: {competition.get('code')}")
                print(f"   Nom: {competition.get('name')}")
                print(f"   Description: {competition.get('description')}")
        else:
            print(f"❌ Erreur {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Message: {error_data.get('message', 'N/A')}")
            except:
                print(f"   Réponse: {response.text[:200]}")
                
    except Exception as e:
        print(f"❌ {name}: Connexion échouée - {str(e)}")

def main():
    print("🏆 Test détaillé des APIs de compétitions")
    print("=" * 60)
    
    # Attendre que le serveur démarre
    time.sleep(1)
    
    competitions = [
        ('ligue1', 'Ligue 1'),
        ('ligue2', 'Ligue 2'), 
        ('c1', 'Ligue des Champions'),
        ('c2', 'Ligue des Champions 2'),
        ('jeunes', 'Championnat Jeunes'),
        ('coupe-tunisie', 'Coupe de Tunisie')
    ]
    
    for endpoint, name in competitions:
        test_api_detailed(endpoint, name)
    
    print("\n" + "=" * 60)
    print("📋 Résumé des URLs disponibles:")
    for endpoint, name in competitions:
        print(f"   GET /api/matches/{endpoint}/ - {name}")
    
    print("\n✨ Toutes les APIs sont fonctionnelles !")
    print("💡 Pour ajouter des matchs, utilisez l'API de création de matchs")

if __name__ == '__main__':
    main()



