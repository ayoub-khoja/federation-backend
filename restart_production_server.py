#!/usr/bin/env python3
"""
Script pour redémarrer le serveur de production et forcer la mise à jour de l'admin
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

def clear_cache():
    """Nettoyer le cache Django"""
    print("🧹 Nettoyage du cache...")
    try:
        # Nettoyer le cache des modèles
        from django.core.cache import cache
        cache.clear()
        print("✅ Cache nettoyé")
    except Exception as e:
        print(f"⚠️  Erreur lors du nettoyage du cache: {e}")

def reload_models():
    """Recharger les modèles"""
    print("🔄 Rechargement des modèles...")
    try:
        # Forcer le rechargement des modèles
        from django.apps import apps
        apps.clear_cache()
        print("✅ Modèles rechargés")
    except Exception as e:
        print(f"⚠️  Erreur lors du rechargement: {e}")

def check_admin_interface():
    """Vérifier l'interface d'administration"""
    print("🔍 Vérification de l'interface d'administration...")
    
    try:
        # Initialiser Django
        django.setup()
        
        from django.contrib import admin
        from accounts.models import GradeArbitrage, LigueArbitrage
        
        print("\n📋 MODÈLES ENREGISTRÉS DANS L'ADMIN:")
        print("-" * 40)
        
        # Lister tous les modèles de l'app accounts
        from accounts import models as accounts_models
        for attr_name in dir(accounts_models):
            attr = getattr(accounts_models, attr_name)
            if hasattr(attr, '_meta') and hasattr(attr._meta, 'app_label'):
                if attr._meta.app_label == 'accounts':
                    is_registered = attr in admin.site._registry
                    status = "✅" if is_registered else "❌"
                    print(f"{status} {attr._meta.verbose_name_plural} ({attr.__name__})")
        
        # Vérifier spécifiquement GradeArbitrage
        if GradeArbitrage in admin.site._registry:
            print(f"\n✅ GradeArbitrage est bien enregistré!")
            print(f"   - Nom d'affichage: {admin.site._registry[GradeArbitrage].model._meta.verbose_name_plural}")
            print(f"   - Classe admin: {admin.site._registry[GradeArbitrage].__class__.__name__}")
        else:
            print("\n❌ GradeArbitrage n'est PAS enregistré!")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")

def main():
    """Fonction principale"""
    print("🚀 REDÉMARRAGE COMPLET DU SERVEUR DE PRODUCTION")
    print("=" * 60)
    
    # Nettoyer le cache
    clear_cache()
    
    # Recharger les modèles
    reload_models()
    
    # Vérifier l'interface d'administration
    check_admin_interface()
    
    print("\n" + "=" * 60)
    print("✅ REDÉMARRAGE TERMINÉ")
    print("=" * 60)
    print("🔄 Actions à effectuer:")
    print("   1. Redémarrez votre serveur de production")
    print("   2. Rafraîchissez votre interface d'administration")
    print("   3. Vérifiez que 'Grades d'arbitrage' apparaît dans le menu")
    print("\n📱 Si le problème persiste, vérifiez les logs du serveur")

if __name__ == "__main__":
    main()
