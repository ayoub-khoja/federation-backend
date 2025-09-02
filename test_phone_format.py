#!/usr/bin/env python3
"""
Test du format +216........ pour les numéros de téléphone
"""
import requests
import json
import random

def test_phone_format():
    # Générer un numéro unique
    phone_suffix = random.randint(10000000, 99999999)
    phone_number = f'216{phone_suffix}'
    
    print(f'Test avec le numéro: {phone_number}')
    print('=== TEST DU FORMAT +216........ ===')
    
    # Tester l'API d'inscription avec tous les champs
    arbitre_url = 'http://localhost:8000/api/accounts/arbitres/register/'
    arbitre_data = {
        'phone_number': phone_number,
        'first_name': 'Ahmed',
        'last_name': 'Ben Ali',
        'email': 'ahmed.benali@example.com',
        'address': '123 Rue de la République, Tunis',
        'profile_photo': None,
        'ligue_id': 22,
        'grade': '2eme_serie',
        'birth_date': '1990-05-15',
        'birth_place': 'Tunis',
        'role': 'arbitre',
        'password': 'testpassword123',
        'password_confirm': 'testpassword123'
    }
    
    try:
        arbitre_response = requests.post(arbitre_url, json=arbitre_data)
        print('Status Code:', arbitre_response.status_code)
        
        if arbitre_response.status_code == 201:
            print('✅ INSCRIPTION RÉUSSIE')
            response_data = arbitre_response.json()
            arbitre_info = response_data['arbitre']
            
            phone_formatted = arbitre_info['phone_number']
            print(f'Numéro de téléphone formaté: {phone_formatted}')
            
            # Vérifier le format
            is_correct_format = phone_formatted.startswith('+216')
            print(f'Format correct: {is_correct_format}')
            
            if is_correct_format:
                print('✅ FORMAT +216........ APPLIQUÉ CORRECTEMENT !')
            else:
                print('❌ FORMAT INCORRECT')
                
            # Afficher tous les champs pour vérification
            print('\n=== DONNÉES COMPLÈTES ===')
            for key, value in arbitre_info.items():
                print(f'{key}: {value}')
                
        else:
            print('❌ ERREUR D\'INSCRIPTION')
            print(json.dumps(arbitre_response.json(), indent=2, ensure_ascii=False))
            
    except Exception as e:
        print('Erreur:', str(e))

if __name__ == '__main__':
    test_phone_format()
