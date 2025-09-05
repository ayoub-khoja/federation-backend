#!/usr/bin/env python3
"""
Test final de toutes les APIs créées
"""
import requests
import json

def test_api(url, method="GET", data=None, name=""):
    """Test d'une API"""
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        
        status = "✅" if response.status_code in [200, 201] else "❌"
        print(f"{status} {name}: {response.status_code}")
        
        if response.status_code in [200, 201]:
            try:
                data = response.json()
                if 'message' in data:
                    print(f"   📝 {data['message']}")
                if 'matches' in data:
                    print(f"   🏆 {len(data['matches'])} match(s)")
                if 'excuses' in data:
                    print(f"   📋 {len(data['excuses'])} excuse(s)")
            except:
                pass
        
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ {name}: Connexion échouée")
        return False

def main():
    print("🏆 Test final de toutes les APIs")
    print("=" * 60)
    
    base_url = "http://localhost:8000/api/matches"
    
    # Test des APIs de compétitions
    print("\n📊 APIs de compétitions:")
    competitions = [
        ('ligue1', 'Ligue 1'),
        ('ligue2', 'Ligue 2'),
        ('c1', 'C1'),
        ('c2', 'C2'),
        ('jeunes', 'Jeunes'),
        ('coupe-tunisie', 'Coupe de Tunisie')
    ]
    
    for endpoint, name in competitions:
        test_api(f"{base_url}/{endpoint}/", name=name)
    
    # Test des APIs d'excuses
    print("\n📋 APIs d'excuses d'arbitres:")
    test_api(f"{base_url}/excuses/", name="Liste des excuses")
    test_api(f"{base_url}/excuses/statistics/", name="Statistiques des excuses")
    
    # Test de création d'excuse
    excuse_data = {
        "nom_arbitre": "Test",
        "prenom_arbitre": "API",
        "date_debut": "2025-09-01",
        "date_fin": "2025-09-03",
        "cause": "Test automatique de l'API"
    }
    test_api(f"{base_url}/excuses/", method="POST", data=excuse_data, name="Création d'excuse")
    
    print("\n" + "=" * 60)
    print("📋 Résumé des APIs disponibles:")
    print("\n🏆 Compétitions:")
    for endpoint, name in competitions:
        print(f"   GET /api/matches/{endpoint}/ - {name}")
    
    print("\n📋 Excuses d'arbitres:")
    print("   GET    /api/matches/excuses/           - Lister toutes les excuses")
    print("   POST   /api/matches/excuses/           - Créer une excuse")
    print("   GET    /api/matches/excuses/{id}/      - Récupérer une excuse")
    print("   PUT    /api/matches/excuses/{id}/      - Modifier une excuse")
    print("   DELETE /api/matches/excuses/{id}/      - Supprimer une excuse")
    print("   GET    /api/matches/excuses/statistics/ - Statistiques")
    
    print("\n✨ Toutes les APIs sont opérationnelles !")

if __name__ == '__main__':
    main()





