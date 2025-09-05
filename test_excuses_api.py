#!/usr/bin/env python3
"""
Test des APIs des excuses d'arbitres
"""
import requests
import json
from datetime import date, timedelta

def test_excuses_api():
    """Tester les APIs des excuses d'arbitres"""
    base_url = "http://localhost:8000/api/matches"
    
    print("🏆 Test des APIs des excuses d'arbitres")
    print("=" * 60)
    
    # Test 1: Lister toutes les excuses (GET)
    print("\n1️⃣ Test GET /api/matches/excuses/")
    try:
        response = requests.get(f"{base_url}/excuses/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Succès: {data.get('message')}")
            print(f"   📊 Nombre d'excuses: {len(data.get('excuses', []))}")
        else:
            print(f"   ❌ Erreur: {response.text}")
    except Exception as e:
        print(f"   ❌ Connexion échouée: {str(e)}")
    
    # Test 2: Créer une excuse (POST)
    print("\n2️⃣ Test POST /api/matches/excuses/")
    excuse_data = {
        "nom_arbitre": "Khoja",
        "prenom_arbitre": "Ayoub",
        "date_debut": "2025-09-01",
        "date_fin": "2025-09-05",
        "cause": "Maladie - Certificat médical fourni"
    }
    
    try:
        response = requests.post(
            f"{base_url}/excuses/",
            json=excuse_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Succès: {data.get('message')}")
            excuse_id = data.get('excuse', {}).get('id')
            print(f"   🆔 ID de l'excuse: {excuse_id}")
        else:
            print(f"   ❌ Erreur: {response.text}")
            excuse_id = None
    except Exception as e:
        print(f"   ❌ Connexion échouée: {str(e)}")
        excuse_id = None
    
    # Test 3: Récupérer une excuse spécifique (GET)
    if excuse_id:
        print(f"\n3️⃣ Test GET /api/matches/excuses/{excuse_id}/")
        try:
            response = requests.get(f"{base_url}/excuses/{excuse_id}/")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Succès: {data.get('message')}")
                excuse = data.get('excuse', {})
                print(f"   👤 Arbitre: {excuse.get('prenom_arbitre')} {excuse.get('nom_arbitre')}")
                print(f"   📅 Période: {excuse.get('date_debut')} au {excuse.get('date_fin')}")
                print(f"   📝 Cause: {excuse.get('cause')}")
            else:
                print(f"   ❌ Erreur: {response.text}")
        except Exception as e:
            print(f"   ❌ Connexion échouée: {str(e)}")
    
    # Test 4: Statistiques des excuses
    print("\n4️⃣ Test GET /api/matches/excuses/statistics/")
    try:
        response = requests.get(f"{base_url}/excuses/statistics/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Succès: {data.get('message')}")
            stats = data.get('statistics', {})
            print(f"   📊 Total excuses: {stats.get('total_excuses')}")
            print(f"   📈 Excuses récentes: {stats.get('recent_excuses')}")
            print(f"   🟢 Excuses actives: {stats.get('active_excuses')}")
        else:
            print(f"   ❌ Erreur: {response.text}")
    except Exception as e:
        print(f"   ❌ Connexion échouée: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📋 URLs disponibles:")
    print("   GET    /api/matches/excuses/           - Lister toutes les excuses")
    print("   POST   /api/matches/excuses/           - Créer une excuse")
    print("   GET    /api/matches/excuses/{id}/      - Récupérer une excuse")
    print("   PUT    /api/matches/excuses/{id}/      - Modifier une excuse")
    print("   DELETE /api/matches/excuses/{id}/      - Supprimer une excuse")
    print("   GET    /api/matches/excuses/statistics/ - Statistiques")

if __name__ == '__main__':
    test_excuses_api()



