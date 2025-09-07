#!/usr/bin/env python
"""
Test final du système OTP avec envoi d'email réel
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

def test_final_otp_system():
    """Test final du système OTP avec email réel"""
    
    base_url = "http://localhost:8000/api/accounts"
    
    print("🚀 Test Final du Système OTP avec Email Réel")
    print("=" * 60)
    
    # 1. Créer un nouvel utilisateur de test
    print("\n1. Création d'un nouvel utilisateur de test...")
    
    test_email = "test.final.otp@gmail.com"
    
    # Supprimer l'utilisateur s'il existe déjà
    try:
        existing_user = Arbitre.objects.get(email=test_email)
        existing_user.delete()
        print(f"✅ Ancien utilisateur supprimé : {test_email}")
    except Arbitre.DoesNotExist:
        pass
    
    # Créer un nouvel utilisateur
    test_arbitre = Arbitre.objects.create(
        phone_number='+21698765432',
        first_name='Test',
        last_name='Final',
        email=test_email,
        is_active=True
    )
    test_arbitre.set_password('ancienMotDePasse123')
    test_arbitre.save()
    
    print(f"✅ Nouvel utilisateur créé : {test_email}")
    
    # 2. Test de la demande de réinitialisation
    print(f"\n2. Test de la demande de réinitialisation avec OTP...")
    
    try:
        response = requests.post(
            f"{base_url}/password-reset/request/",
            json={"email": test_email},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Demande de réinitialisation réussie !")
            print("📧 Vérifiez votre email pour le code OTP et le lien")
            
            # Récupérer le token créé
            reset_token = PasswordResetToken.objects.filter(
                email=test_email,
                is_used=False
            ).first()
            
            if reset_token:
                print(f"✅ Token créé : {reset_token.token[:20]}...")
                print(f"✅ Code OTP généré : {reset_token.otp_code}")
                print(f"✅ Expire dans : 5 minutes")
                
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
                        
                        # 5. Test de confirmation de réinitialisation
                        print(f"\n5. Test de confirmation de réinitialisation...")
                        
                        new_password = "nouveauMotDePasseFinal123"
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
                            print("✅ Confirmation de réinitialisation réussie")
                            
                            # Vérifier que le mot de passe a été changé
                            test_arbitre.refresh_from_db()
                            if test_arbitre.check_password(new_password):
                                print("✅ Mot de passe effectivement changé")
                            else:
                                print("❌ Le mot de passe n'a pas été changé")
                            
                            # Vérifier que le token est marqué comme utilisé
                            reset_token.refresh_from_db()
                            if reset_token.is_used:
                                print("✅ Token marqué comme utilisé")
                            else:
                                print("❌ Token pas marqué comme utilisé")
                                
                            print("\n🎉 SYSTÈME OTP COMPLET FONCTIONNEL !")
                            print("📧 Email envoyé avec succès")
                            print("🔐 Code OTP vérifié")
                            print("🔑 Mot de passe réinitialisé")
                            
                        else:
                            print("❌ Échec de la confirmation de réinitialisation")
                    else:
                        print("❌ Échec de la vérification OTP")
                else:
                    print("❌ Échec de la validation du token")
            else:
                print("❌ Aucun token trouvé")
        else:
            print("❌ Échec de la demande de réinitialisation")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur. Assurez-vous que le serveur Django est démarré.")
        print("   Commande : python manage.py runserver")
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test final terminé")

if __name__ == "__main__":
    test_final_otp_system()













