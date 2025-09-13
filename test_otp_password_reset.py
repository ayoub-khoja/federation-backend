#!/usr/bin/env python
"""
Script de test pour l'API de réinitialisation de mot de passe avec OTP
"""
import os
import sys
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import Arbitre, PasswordResetToken
from django.contrib.auth import get_user_model

def test_otp_password_reset_api():
    """Test complet de l'API de réinitialisation de mot de passe avec OTP"""
    
    base_url = "http://localhost:8000/api/accounts"
    
    print("🔐 Test de l'API de réinitialisation de mot de passe avec OTP")
    print("=" * 70)
    
    # 1. Vérifier qu'il y a au moins un utilisateur avec un email
    print("\n1. Vérification des utilisateurs existants...")
    
    arbitre_with_email = Arbitre.objects.filter(email__isnull=False, email__gt='').first()
    
    if not arbitre_with_email:
        print("❌ Aucun arbitre avec email trouvé. Créons un utilisateur de test...")
        
        # Créer un utilisateur de test
        test_arbitre = Arbitre.objects.create(
            phone_number='+21612345678',
            first_name='Test',
            last_name='User',
            email='test.otp@example.com',
            is_active=True
        )
        test_arbitre.set_password('ancienMotDePasse123')
        test_arbitre.save()
        
        print(f"✅ Utilisateur de test créé : {test_arbitre.email}")
        test_email = test_arbitre.email
    else:
        test_email = arbitre_with_email.email
        print(f"✅ Utilisateur trouvé : {test_email}")
    
    # 2. Test de la demande de réinitialisation avec OTP
    print(f"\n2. Test de la demande de réinitialisation avec OTP pour {test_email}...")
    
    try:
        response = requests.post(
            f"{base_url}/password-reset/request/",
            json={"email": test_email},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Demande de réinitialisation avec OTP réussie")
            
            # Récupérer le token créé
            reset_token = PasswordResetToken.objects.filter(
                email=test_email,
                is_used=False
            ).first()
            
            if reset_token:
                print(f"✅ Token créé : {reset_token.token[:20]}...")
                print(f"✅ Code OTP généré : {reset_token.otp_code}")
                print(f"✅ OTP vérifié : {reset_token.otp_verified}")
                
                # 3. Test de validation du token
                print(f"\n3. Test de validation du token...")
                
                validate_response = requests.get(
                    f"{base_url}/password-reset/validate/{reset_token.token}/"
                )
                
                print(f"Status Code: {validate_response.status_code}")
                print(f"Response: {json.dumps(validate_response.json(), indent=2, ensure_ascii=False)}")
                
                if validate_response.status_code == 200:
                    print("✅ Validation du token réussie")
                    
                    # 4. Test de vérification du code OTP
                    print(f"\n4. Test de vérification du code OTP...")
                    
                    otp_verify_response = requests.post(
                        f"{base_url}/password-reset/verify-otp/",
                        json={
                            "token": reset_token.token,
                            "otp_code": reset_token.otp_code
                        },
                        headers={"Content-Type": "application/json"}
                    )
                    
                    print(f"Status Code: {otp_verify_response.status_code}")
                    print(f"Response: {json.dumps(otp_verify_response.json(), indent=2, ensure_ascii=False)}")
                    
                    if otp_verify_response.status_code == 200:
                        print("✅ Vérification OTP réussie")
                        
                        # Vérifier que l'OTP est marqué comme vérifié
                        reset_token.refresh_from_db()
                        if reset_token.otp_verified:
                            print("✅ OTP marqué comme vérifié")
                        else:
                            print("❌ OTP pas marqué comme vérifié")
                        
                        # 5. Test de confirmation de réinitialisation avec OTP vérifié
                        print(f"\n5. Test de confirmation de réinitialisation avec OTP vérifié...")
                        
                        new_password = "nouveauMotDePasseOTP123"
                        confirm_response = requests.post(
                            f"{base_url}/password-reset/confirm/",
                            json={
                                "token": reset_token.token,
                                "new_password": new_password,
                                "confirm_password": new_password
                            },
                            headers={"Content-Type": "application/json"}
                        )
                        
                        print(f"Status Code: {confirm_response.status_code}")
                        print(f"Response: {json.dumps(confirm_response.json(), indent=2, ensure_ascii=False)}")
                        
                        if confirm_response.status_code == 200:
                            print("✅ Confirmation de réinitialisation avec OTP réussie")
                            
                            # Vérifier que le mot de passe a été changé
                            arbitre_with_email.refresh_from_db()
                            if arbitre_with_email.check_password(new_password):
                                print("✅ Mot de passe effectivement changé")
                            else:
                                print("❌ Le mot de passe n'a pas été changé")
                            
                            # Vérifier que le token est marqué comme utilisé
                            reset_token.refresh_from_db()
                            if reset_token.is_used:
                                print("✅ Token marqué comme utilisé")
                            else:
                                print("❌ Token pas marqué comme utilisé")
                                
                        else:
                            print("❌ Échec de la confirmation de réinitialisation avec OTP")
                    else:
                        print("❌ Échec de la vérification OTP")
                else:
                    print("❌ Échec de la validation du token")
            else:
                print("❌ Aucun token trouvé")
        else:
            print("❌ Échec de la demande de réinitialisation avec OTP")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur. Assurez-vous que le serveur Django est démarré.")
        print("   Commande : python manage.py runserver")
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
    
    # 6. Test avec un code OTP incorrect
    print(f"\n6. Test avec un code OTP incorrect...")
    
    try:
        # Créer un nouveau token pour ce test
        test_arbitre = Arbitre.objects.filter(email=test_email).first()
        if test_arbitre:
            reset_token = PasswordResetToken.create_for_user(
                user=test_arbitre,
                email=test_email
            )
            
            otp_verify_response = requests.post(
                f"{base_url}/password-reset/verify-otp/",
                json={
                    "token": reset_token.token,
                    "otp_code": "000000"  # Code OTP incorrect
                },
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {otp_verify_response.status_code}")
            print(f"Response: {json.dumps(otp_verify_response.json(), indent=2, ensure_ascii=False)}")
            
            if otp_verify_response.status_code == 400:
                print("✅ Gestion correcte du code OTP incorrect")
            else:
                print("❌ Gestion incorrecte du code OTP incorrect")
                
    except Exception as e:
        print(f"❌ Erreur lors du test OTP incorrect : {e}")
    
    # 7. Test avec un email inexistant
    print(f"\n7. Test avec un email inexistant...")
    
    try:
        response = requests.post(
            f"{base_url}/password-reset/request/",
            json={"email": "inexistant.otp@example.com"},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 404:
            print("✅ Gestion correcte de l'email inexistant")
        else:
            print("❌ Gestion incorrecte de l'email inexistant")
            
    except Exception as e:
        print(f"❌ Erreur lors du test email inexistant : {e}")
    
    print("\n" + "=" * 70)
    print("🏁 Test du système OTP terminé")

if __name__ == "__main__":
    test_otp_password_reset_api()















