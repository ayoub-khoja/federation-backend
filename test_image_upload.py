#!/usr/bin/env python3
"""
Script de test pour l'upload d'image de profil
"""

import os
import sys
import django
import requests
from pathlib import Path

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

def test_image_upload():
    """Tester l'upload d'image de profil"""
    
    print("🧪 TEST D'UPLOAD D'IMAGE DE PROFIL")
    print("=" * 50)
    
    # URL de l'API
    api_url = "http://localhost:8000/api/accounts/arbitres/register/"
    
    # Créer un fichier de test (image simple)
    test_image_path = "test_image.png"
    
    # Créer une image de test simple (1x1 pixel PNG)
    try:
        # Créer un fichier PNG minimal
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf6\x178U\x00\x00\x00\x00IEND\xaeB`\x82'
        
        with open(test_image_path, 'wb') as f:
            f.write(png_data)
        
        print(f"✅ Image de test créée: {test_image_path}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'image de test: {e}")
        return False
    
    try:
        # Préparer les données de test
        test_data = {
            'phone_number': '+21612345681',
            'first_name': 'Test',
            'last_name': 'Image',
            'email': 'test.image@example.com',
            'address': 'Test Address',
            'ligue_id': 2,
            'grade': 'candidat',
            'birth_date': '1990-01-01',
            'birth_place': 'Test City',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        # Créer FormData
        files = {'profile_photo': open(test_image_path, 'rb')}
        
        print("📤 Envoi de la requête avec image...")
        
        # Envoyer la requête
        response = requests.post(api_url, data=test_data, files=files)
        
        print(f"📊 Statut de la réponse: {response.status_code}")
        print(f"📄 Contenu de la réponse: {response.text}")
        
        if response.status_code == 201:
            print("✅ Test réussi ! L'image de profil a été uploadée.")
            
            # Nettoyer le fichier de test
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
                print(f"🧹 Fichier de test supprimé: {test_image_path}")
            
            return True
        else:
            print(f"❌ Test échoué. Statut: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        
        # Nettoyer le fichier de test
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        
        return False

if __name__ == "__main__":
    success = test_image_upload()
    sys.exit(0 if success else 1)
