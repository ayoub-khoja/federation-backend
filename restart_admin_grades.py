#!/usr/bin/env python3
"""
Script pour redémarrer l'interface d'administration avec les grades
"""

import os
import sys
import django
from pathlib import Path

# Ajouter le répertoire backend au path Python
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configuration de l'environnement Django pour la production
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings_production')

# Initialiser Django
django.setup()

def check_admin_registration():
    """Vérifier l'enregistrement des modèles dans l'admin"""
    from django.contrib import admin
    from accounts.models import GradeArbitrage, LigueArbitrage
    
    print("🔍 VÉRIFICATION DE L'ENREGISTREMENT ADMIN")
    print("=" * 50)
    
    # Vérifier GradeArbitrage
    if GradeArbitrage in admin.site._registry:
        print("✅ GradeArbitrage est enregistré dans l'admin")
        grade_admin = admin.site._registry[GradeArbitrage]
        print(f"   - Classe admin: {grade_admin.__class__.__name__}")
        print(f"   - Nom d'affichage: {grade_admin.model._meta.verbose_name_plural}")
    else:
        print("❌ GradeArbitrage N'EST PAS enregistré dans l'admin")
    
    # Vérifier LigueArbitrage pour comparaison
    if LigueArbitrage in admin.site._registry:
        print("✅ LigueArbitrage est enregistré dans l'admin")
        ligue_admin = admin.site._registry[LigueArbitrage]
        print(f"   - Classe admin: {ligue_admin.__class__.__name__}")
        print(f"   - Nom d'affichage: {ligue_admin.model._meta.verbose_name_plural}")
    else:
        print("❌ LigueArbitrage N'EST PAS enregistré dans l'admin")
    
    print("\n📋 TOUS LES MODÈLES ENREGISTRÉS:")
    for model, admin_class in admin.site._registry.items():
        if hasattr(model, '_meta') and 'arbitrage' in str(model._meta.app_label).lower():
            print(f"   - {model._meta.verbose_name_plural} ({model.__name__})")

def force_register_grades():
    """Forcer l'enregistrement des grades"""
    from django.contrib import admin
    from accounts.models import GradeArbitrage
    from accounts.admin import GradeArbitrageAdmin
    
    print("\n🔧 FORÇAGE DE L'ENREGISTREMENT DES GRADES")
    print("=" * 50)
    
    # Désenregistrer si déjà enregistré
    if GradeArbitrage in admin.site._registry:
        admin.site.unregister(GradeArbitrage)
        print("   - GradeArbitrage désenregistré")
    
    # Réenregistrer
    admin.site.register(GradeArbitrage, GradeArbitrageAdmin)
    print("   - GradeArbitrage réenregistré avec GradeArbitrageAdmin")
    
    # Vérifier
    if GradeArbitrage in admin.site._registry:
        print("✅ GradeArbitrage est maintenant enregistré")
    else:
        print("❌ Échec de l'enregistrement de GradeArbitrage")

def main():
    """Fonction principale"""
    print("🚀 REDÉMARRAGE DE L'INTERFACE D'ADMINISTRATION")
    print("=" * 60)
    
    # Vérifier l'état actuel
    check_admin_registration()
    
    # Forcer l'enregistrement
    force_register_grades()
    
    # Vérifier à nouveau
    print("\n🔍 VÉRIFICATION FINALE")
    print("=" * 30)
    check_admin_registration()
    
    print("\n✅ Redémarrage terminé!")
    print("🔄 Rafraîchissez votre interface d'administration")

if __name__ == "__main__":
    main()
