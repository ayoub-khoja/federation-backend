#!/usr/bin/env python3
"""
Script de test de connectivité pour vérifier si le serveur backend est accessible
"""

import requests
import json
import sys
from datetime import datetime

def test_backend_connectivity():
    """Test de connectivité du backend"""
    
    # URLs à tester
    urls_to_test = [
        "http://localhost:8000/api/accounts/arbitre/login/",
        "https://federation-backend.onrender.com/api/accounts/arbitre/login/",
    ]
    
    print("🔍 Test de connectivité du backend")
    print("=" * 50)
    
    for url in urls_to_test:
        print(f"\n🌐 Test de l'URL: {url}")
        try:
            # Test avec une requête OPTIONS (CORS preflight)
            response = requests.options(url, timeout=10)
            print(f"✅ OPTIONS - Status: {response.status_code}")
            print(f"   Headers CORS: {dict(response.headers)}")
            
            # Test avec une requête POST (connexion)
            test_data = {
                "phone_number": "+21612345678",
                "password": "test123"
            }
            
            response = requests.post(
                url, 
                json=test_data, 
                headers={
                    'Content-Type': 'application/json',
                    'Origin': 'https://federation-mobile.vercel.app'
                },
                timeout=10
            )
            
            print(f"✅ POST - Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Erreur de connexion: {e}")
            print("   → Vérifiez que le serveur est démarré")
            print("   → Commande: python manage.py runserver")
            
        except requests.exceptions.Timeout as e:
            print(f"⏰ Timeout: {e}")
            print("   → Le serveur met trop de temps à répondre")
            
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test terminé")

def test_database_connection():
    """Test de connexion à la base de données"""
    print("\n🗄️ Test de connexion à la base de données")
    print("=" * 50)
    
    try:
        import os
        import django
        from django.conf import settings
        
        # Configuration Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
        django.setup()
        
        from django.db import connection
        from accounts.models import Arbitre
        
        # Test de connexion
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"✅ Connexion DB réussie: {result}")
        
        # Test de lecture des données
        arbitres_count = Arbitre.objects.count()
        print(f"✅ Nombre d'arbitres en base: {arbitres_count}")
        
        # Test d'un arbitre spécifique
        try:
            arbitre = Arbitre.objects.first()
            if arbitre:
                print(f"✅ Premier arbitre trouvé: {arbitre.get_full_name()}")
            else:
                print("⚠️ Aucun arbitre trouvé en base")
        except Exception as e:
            print(f"❌ Erreur lors de la lecture des arbitres: {e}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")

if __name__ == "__main__":
    print(f"🕐 Test démarré à: {datetime.now()}")
    
    # Test de connectivité réseau
    test_backend_connectivity()
    
    # Test de base de données
    test_database_connection()
    
    print(f"\n🕐 Test terminé à: {datetime.now()}")



