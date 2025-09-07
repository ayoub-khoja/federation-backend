#!/usr/bin/env python3
"""
Script de déploiement pour corriger l'erreur 500 des news
"""

import os
import sys
import django
from django.conf import settings

def setup_django():
    """Configuration Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings_production')
    django.setup()

def run_migrations():
    """Exécuter les migrations"""
    print("🔄 Exécution des migrations...")
    
    try:
        from django.core.management import execute_from_command_line
        
        # Vérifier les migrations en attente
        execute_from_command_line(['manage.py', 'showmigrations', 'news'])
        
        # Appliquer les migrations
        execute_from_command_line(['manage.py', 'migrate', 'news', '--noinput'])
        
        print("✅ Migrations appliquées avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des migrations: {e}")
        return False

def fix_news_data():
    """Corriger les données des news"""
    print("🔧 Correction des données des news...")
    
    try:
        from news.models import News
        from django.contrib.contenttypes.models import ContentType
        from accounts.models import Admin
        
        # Créer un admin par défaut pour les news sans auteur
        default_admin, created = Admin.objects.get_or_create(
            phone_number="+216000000000",
            defaults={
                'first_name': 'Système',
                'last_name': 'Administrateur',
                'email': 'system@arbitrage.tn',
                'is_active': True
            }
        )
        
        if created:
            print(f"✅ Admin par défaut créé: {default_admin.get_full_name()}")
        else:
            print(f"✅ Admin par défaut existant: {default_admin.get_full_name()}")
        
        # Obtenir le ContentType pour Admin
        admin_content_type = ContentType.objects.get_for_model(Admin)
        
        # Corriger les news sans auteur
        news_without_author = News.objects.filter(content_type__isnull=True)
        count = news_without_author.count()
        
        if count > 0:
            print(f"📊 Correction de {count} news sans auteur...")
            
            for news in news_without_author:
                news.content_type = admin_content_type
                news.object_id = default_admin.id
                news.save()
                print(f"   ✅ News '{news.title_fr}' corrigée")
            
            print(f"🎉 {count} news corrigées avec succès")
        else:
            print("✅ Toutes les news ont déjà un auteur")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction des données: {e}")
        return False

def test_admin_access():
    """Tester l'accès à l'admin des news"""
    print("🔍 Test de l'accès à l'admin des news...")
    
    try:
        from news.models import News
        from news.admin import NewsAdmin
        
        # Tester l'admin
        admin = NewsAdmin(News, None)
        
        # Tester les requêtes
        total_news = News.objects.count()
        print(f"📊 Total des news: {total_news}")
        
        # Tester l'affichage des auteurs
        for news in News.objects.all()[:3]:
            author_name = admin.get_author_name(news)
            print(f"   - {news.title_fr}: {author_name}")
        
        print("✅ L'admin des news fonctionne correctement")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de l'admin: {e}")
        return False

def collect_static():
    """Collecter les fichiers statiques"""
    print("📁 Collecte des fichiers statiques...")
    
    try:
        from django.core.management import execute_from_command_line
        
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        
        print("✅ Fichiers statiques collectés avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la collecte des fichiers statiques: {e}")
        return False

def main():
    """Fonction principale"""
    print("🏁 Déploiement de la correction des news")
    print("=" * 60)
    
    # Configuration Django
    setup_django()
    
    # Étapes de déploiement
    steps = [
        ("Migrations", run_migrations),
        ("Correction des données", fix_news_data),
        ("Test de l'admin", test_admin_access),
        ("Collecte des fichiers statiques", collect_static),
    ]
    
    success = True
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ Échec de l'étape: {step_name}")
            success = False
        else:
            print(f"✅ {step_name} terminé avec succès")
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Déploiement terminé avec succès!")
        print("🌐 L'admin des news devrait maintenant fonctionner sans erreur 500")
        print("🔗 URL: https://federation-backend.onrender.com/admin/news/news/")
    else:
        print("❌ Le déploiement a échoué")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
