#!/usr/bin/env python3
"""
Test du format +216........ avec différents formats d'entrée
"""
import requests
import json
import random

def test_different_phone_formats():
    """Test avec différents formats de numéros de téléphone"""
    
    # Formats à tester
    test_cases = [
        ("21612345678", "Format 216XXXXXXXX"),
        ("012345678", "Format 0XXXXXXXX"),
        ("12345678", "Format XXXXXXXXX (8 chiffres)"),
        ("+21612345678", "Format +216XXXXXXXX"),
    ]
    
    for phone_input, description in test_cases:
        print(f"\n=== TEST: {description} ===")
        print(f"Entrée: {phone_input}")
        
        # Générer un numéro unique pour éviter les conflits
        phone_suffix = random.randint(10000000, 99999999)
        if phone_input.startswith("216"):
            test_phone = f"216{phone_suffix}"
        elif phone_input.startswith("0"):
            test_phone = f"0{phone_suffix}"
        elif phone_input.startswith("+216"):
            test_phone = f"+216{phone_suffix}"
        else:
            test_phone = str(phone_suffix)
        
        print(f"Numéro de test: {test_phone}")
        
        # Tester l'API d'inscription
        arbitre_url = 'http://localhost:8000/api/accounts/arbitres/register/'
        arbitre_data = {
            'phone_number': test_phone,
            'first_name': f'Test{phone_suffix}',
            'last_name': 'Format',
            'email': f'test{phone_suffix}@example.com',
            'address': 'Test Address',
            'profile_photo': None,
            'ligue_id': 22,
            'grade': '2eme_serie',
            'birth_date': '1990-01-01',
            'birth_place': 'Test',
            'role': 'arbitre',
            'password': 'testpassword123',
            'password_confirm': 'testpassword123'
        }
        
        try:
            arbitre_response = requests.post(arbitre_url, json=arbitre_data)
            
            if arbitre_response.status_code == 201:
                response_data = arbitre_response.json()
                arbitre_info = response_data['arbitre']
                formatted_phone = arbitre_info['phone_number']
                
                print(f"✅ SUCCÈS - Formaté: {formatted_phone}")
                
                # Vérifier le format
                if formatted_phone.startswith('+216'):
                    print("✅ FORMAT +216........ CORRECT")
                else:
                    print("❌ FORMAT INCORRECT")
                    
            else:
                print(f"❌ ERREUR - Status: {arbitre_response.status_code}")
                try:
                    error_data = arbitre_response.json()
                    if 'errors' in error_data:
                        print(f"Erreur: {error_data['errors']}")
                except:
                    print("Erreur de parsing de la réponse")
                    
        except Exception as e:
            print(f"Exception: {str(e)}")

if __name__ == '__main__':
    test_different_phone_formats()
