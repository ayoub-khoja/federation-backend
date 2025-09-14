#!/usr/bin/env python
"""
Test de l'API de notification de désignation
"""
import os
import sys
import django
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from accounts.models import Admin, Arbitre
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.views import notify_arbitre_designation

def test_api_notification():
    """Test de l'API de notification"""
    print("🧪 Test de l'API de notification de désignation")
    print("=" * 60)
    
    # 1. Récupérer un admin
    admin = Admin.objects.first()
    if not admin:
        print("❌ Aucun admin trouvé")
        return
    
    print(f"✅ Admin trouvé: {admin.get_full_name()} (ID: {admin.id})")
    
    # 2. Générer un token JWT pour l'admin
    refresh = RefreshToken.for_user(admin)
    access_token = str(refresh.access_token)
    print(f"✅ Token JWT généré: {access_token[:20]}...")
    
    # 3. Récupérer un arbitre
    arbitre = Arbitre.objects.get(id=28)
    print(f"✅ Arbitre trouvé: {arbitre.get_full_name()} (ID: {arbitre.id})")
    
    # 4. Préparer les données de test
    test_data = {
        "arbitre_id": 28,
        "arbitre_nom": "ayoub ramez khouja",
        "arbitre_email": "ayoub@example.com",
        "match_id": 1,
        "match_nom": "ess vs est",
        "match_date": "2024-01-15T14:00:00Z",
        "match_lieu": "Stade Municipal",
        "designation_type": "arbitre_principal",
        "message": "Vous avez été désigné comme arbitre principal"
    }
    
    print(f"📋 Données de test: {json.dumps(test_data, indent=2)}")
    
    # 5. Créer une requête simulée
    factory = RequestFactory()
    request = factory.post(
        '/api/accounts/arbitres/notify-designation/',
        data=json.dumps(test_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    
    # 6. Simuler l'utilisateur authentifié
    request.user = admin
    
    # 7. Appeler la vue
    print("\n📤 Appel de l'API...")
    try:
        response = notify_arbitre_designation(request)
        print(f"✅ Réponse HTTP: {response.status_code}")
        print(f"📄 Contenu: {response.data}")
        
        if response.status_code == 200:
            print("🎉 API fonctionne correctement!")
        else:
            print(f"⚠️ Erreur API: {response.data}")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'appel API: {e}")
        import traceback
        traceback.print_exc()

def test_with_client():
    """Test avec le client Django"""
    print("\n" + "=" * 60)
    print("🧪 Test avec le client Django")
    print("=" * 60)
    
    # 1. Récupérer un admin
    admin = Admin.objects.first()
    if not admin:
        print("❌ Aucun admin trouvé")
        return
    
    # 2. Générer un token JWT
    refresh = RefreshToken.for_user(admin)
    access_token = str(refresh.access_token)
    
    # 3. Créer le client
    client = Client()
    
    # 4. Préparer les données
    test_data = {
        "arbitre_id": 28,
        "arbitre_nom": "ayoub ramez khouja",
        "arbitre_email": "ayoub@example.com",
        "match_id": 1,
        "match_nom": "ess vs est",
        "match_date": "2024-01-15T14:00:00Z",
        "match_lieu": "Stade Municipal",
        "designation_type": "arbitre_principal",
        "message": "Vous avez été désigné comme arbitre principal"
    }
    
    # 5. Faire la requête
    print("📤 Requête avec le client Django...")
    response = client.post(
        '/api/accounts/arbitres/notify-designation/',
        data=json.dumps(test_data),
        content_type='application/json',
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    
    print(f"✅ Statut: {response.status_code}")
    print(f"📄 Contenu: {response.content.decode()}")
    
    if response.status_code == 200:
        print("🎉 API fonctionne avec le client Django!")
    else:
        print(f"⚠️ Erreur: {response.content.decode()}")

if __name__ == "__main__":
    test_api_notification()
    test_with_client()


















