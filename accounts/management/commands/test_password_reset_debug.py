from django.core.management.base import BaseCommand
from django.test import Client
from accounts.models import PasswordResetToken, Arbitre
import json

class Command(BaseCommand):
    help = 'Test automatique pour déboguer le problème de réinitialisation de mot de passe'

    def handle(self, *args, **options):
        """Test automatique complet du flux de réinitialisation de mot de passe"""
        
        self.stdout.write(self.style.SUCCESS('🔍 Test automatique de réinitialisation de mot de passe'))
        self.stdout.write('=' * 60)
        
        EMAIL = "ayoubramezkhoja2003@gmail.com"
        client = Client()
        
        # Étape 1: Demander la réinitialisation
        self.stdout.write('\n1️⃣ Demande de réinitialisation...')
        response = client.post('/api/accounts/password-reset/request/', {
            'email': EMAIL
        })
        
        self.stdout.write(f"Status: {response.status_code}")
        self.stdout.write(f"Response: {response.json()}")
        
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR('❌ Échec de la demande de réinitialisation'))
            return
        
        # Étape 2: Récupérer le token et OTP depuis la base de données
        self.stdout.write('\n2️⃣ Récupération du token et OTP depuis la base de données...')
        
        try:
            latest_token = PasswordResetToken.objects.filter(
                email=EMAIL,
                is_used=False
            ).order_by('-created_at').first()
            
            if not latest_token:
                self.stdout.write(self.style.ERROR('❌ Aucun token trouvé dans la base de données'))
                return
            
            token = latest_token.token
            otp_code = latest_token.otp_code
            
            self.stdout.write(self.style.SUCCESS(f'✅ Token trouvé: {token[:20]}...'))
            self.stdout.write(self.style.SUCCESS(f'✅ Code OTP: {otp_code}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erreur lors de la récupération du token: {e}'))
            return
        
        # Étape 3: Vérifier l'OTP
        self.stdout.write('\n3️⃣ Vérification du code OTP...')
        response = client.post('/api/accounts/password-reset/verify-otp/', {
            'token': token,
            'otp_code': otp_code
        })
        
        self.stdout.write(f"Status: {response.status_code}")
        self.stdout.write(f"Response: {response.json()}")
        
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR('❌ Échec de la vérification OTP'))
            return
        
        # Étape 4: Confirmer la réinitialisation
        self.stdout.write('\n4️⃣ Confirmation de la réinitialisation...')
        new_password = "NouveauMotDePasse123!"
        
        response = client.post('/api/accounts/password-reset/confirm/', {
            'token': token,
            'new_password': new_password,
            'confirm_password': new_password
        })
        
        self.stdout.write(f"Status: {response.status_code}")
        self.stdout.write(f"Response: {response.json()}")
        
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS('✅ Réinitialisation réussie!'))
            self.stdout.write(f'🔍 Nouveau mot de passe: {new_password}')
            
            # Étape 5: Vérifier que le mot de passe a vraiment changé
            self.stdout.write('\n5️⃣ Vérification du changement de mot de passe...')
            
            try:
                # Récupérer l'utilisateur depuis la base de données
                user = Arbitre.objects.get(email=EMAIL)
                self.stdout.write(f'🔍 Utilisateur trouvé: {user.first_name} {user.last_name}')
                self.stdout.write(f'🔍 Mot de passe actuel (hash): {user.password}')
                
                # Tester la connexion avec le nouveau mot de passe
                self.stdout.write('\n🔍 Test avec le nouveau mot de passe...')
                new_password_test = user.check_password(new_password)
                self.stdout.write(f'🔍 Nouveau mot de passe valide: {new_password_test}')
                
                if new_password_test:
                    self.stdout.write(self.style.SUCCESS('✅ Le mot de passe a été correctement changé!'))
                else:
                    self.stdout.write(self.style.ERROR('❌ Le mot de passe n\'a PAS été changé!'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Erreur lors de la vérification: {e}'))
        else:
            self.stdout.write(self.style.ERROR('❌ Échec de la confirmation'))






