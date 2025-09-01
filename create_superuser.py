import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import Arbitre

def create_superuser():
    """Créer un superuser pour l'administration"""
    try:
        # Vérifier si un superuser existe déjà
        if Arbitre.objects.filter(is_superuser=True).exists():
            print("✅ Un superuser existe déjà")
            return
        
        # Créer le superuser
        superuser = Arbitre.objects.create_superuser(
            phone_number='+21699999999',
            password='admin123456',
            first_name='Admin',
            last_name='System',
            email='admin@example.com',
            grade='federale'
        )
        
        print(f"✅ Superuser créé avec succès!")
        print(f"📱 Numéro de téléphone: {superuser.phone_number}")
        print(f"🔑 Mot de passe: admin123456")
        print(f"👤 Nom complet: {superuser.get_full_name()}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création du superuser: {e}")

if __name__ == '__main__':
    create_superuser()
