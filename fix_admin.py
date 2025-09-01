#!/usr/bin/env python
"""
Script pour corriger les permissions de l'admin
"""
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import Admin

def fix_admin_permissions():
    """Corriger les permissions de l'admin"""
    
    print("🔧 CORRECTION DES PERMISSIONS ADMIN")
    print("=" * 50)
    
    # Récupérer l'admin
    try:
        admin = Admin.objects.first()
        if admin:
            print(f"📋 Admin trouvé: {admin.get_full_name()} ({admin.phone_number})")
            print(f"   Avant: Staff={admin.is_staff}, Superuser={admin.is_superuser}")
            
            # Corriger les permissions
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            
            print(f"   Après: Staff={admin.is_staff}, Superuser={admin.is_superuser}")
            print("✅ Permissions corrigées avec succès!")
            
            # Vérifier les permissions
            print(f"\n🔐 VÉRIFICATION DES PERMISSIONS")
            print(f"   - is_authenticated: {admin.is_authenticated}")
            print(f"   - is_active: {admin.is_active}")
            print(f"   - is_staff: {admin.is_staff}")
            print(f"   - is_superuser: {admin.is_superuser}")
            
        else:
            print("❌ Aucun admin trouvé dans la base de données")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    fix_admin_permissions()
