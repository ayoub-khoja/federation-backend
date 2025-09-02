#!/usr/bin/env python3
"""
Script pour activer l'arbitre de test
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import Arbitre

def activate_test_arbitre():
    """Activer l'arbitre de test"""
    
    print("🔧 Activation de l'arbitre de test...")
    
    try:
        # Récupérer l'arbitre de test
        arbitre = Arbitre.objects.get(phone_number="+21612345678")
        
        print(f"✅ Arbitre trouvé: {arbitre.first_name} {arbitre.last_name}")
        print(f"   📱 Téléphone: {arbitre.phone_number}")
        print(f"   🔒 Statut actif: {arbitre.is_active}")
        print(f"   👤 Staff: {arbitre.is_staff}")
        print(f"   🚀 Superuser: {arbitre.is_superuser}")
        
        # Activer l'arbitre
        arbitre.is_active = True
        arbitre.save()
        
        print(f"✅ Arbitre activé avec succès!")
        
        # Vérifier le statut après activation
        arbitre.refresh_from_db()
        print(f"   🔒 Nouveau statut actif: {arbitre.is_active}")
        
        return arbitre
        
    except Arbitre.DoesNotExist:
        print("❌ Arbitre de test non trouvé")
        return None
    except Exception as e:
        print(f"❌ Erreur lors de l'activation: {e}")
        return None

def test_login_again():
    """Tester à nouveau la connexion de l'arbitre"""
    
    print("\n🔐 Test de connexion de l'arbitre (après activation)...")
    
    try:
        from django.contrib.auth import authenticate
        
        arbitre = authenticate(
            phone_number="+21612345678",
            password="test123456"
        )
        
        if arbitre:
            print("✅ Authentification réussie!")
            print(f"   👤 Nom: {arbitre.first_name} {arbitre.last_name}")
            print(f"   📱 Téléphone: {arbitre.phone_number}")
            print(f"   ⚽ Grade: {arbitre.grade}")
            print(f"   🔒 Statut actif: {arbitre.is_active}")
        else:
            print("❌ Authentification échouée")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("🔧 ACTIVATION DE L'ARBITRE DE TEST")
    print("=" * 50)
    
    arbitre = activate_test_arbitre()
    
    if arbitre:
        test_login_again()
    
    print("\n" + "=" * 50)
    print("🏁 Script terminé")
    print("=" * 50)

















