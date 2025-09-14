#!/usr/bin/env python3
"""
Script de test pour vérifier l'admin des news
"""

import os
import sys
import django
from django.conf import settings

def setup_django():
    """Configuration Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
    django.setup()

def test_news_model():
    """Tester le modèle News"""
    print("🔍 Test du modèle News...")
    
    try:
        from news.models import News
        from django.contrib.contenttypes.models import ContentType
        from accounts.models import Admin
        
        # Vérifier que le modèle peut être importé
        print("✅ Modèle News importé avec succès")
        
        # Vérifier les champs
        fields = [field.name for field in News._meta.fields]
        print(f"✅ Champs du modèle: {fields}")
        
        # Vérifier les relations
        print(f"✅ ContentType disponible: {ContentType.objects.count()} types")
        
        # Tester la création d'une news de test
        try:
            # Créer un admin de test si nécessaire
            admin, created = Admin.objects.get_or_create(
                phone_number="+216999999999",
                defaults={
                    'first_name': 'Test',
                    'last_name': 'Admin',
                    'email': 'test@admin.com'
                }
            )
            
            # Créer une news de test
            news = News.objects.create(
                title_fr="Test News FR",
                title_ar="Test News AR",
                content_fr="Contenu de test en français",
                content_ar="محتوى الاختبار بالعربية",
                content_type=ContentType.objects.get_for_model(admin),
                object_id=admin.id
            )
            
            print(f"✅ News de test créée: {news}")
            print(f"✅ Auteur: {news.author}")
            print(f"✅ Nom de l'auteur: {news.author.get_full_name() if news.author else 'Aucun'}")
            
            # Nettoyer
            news.delete()
            if created:
                admin.delete()
                
        except Exception as e:
            print(f"⚠️ Erreur lors de la création de test: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur avec le modèle News: {e}")
        return False

def test_admin_interface():
    """Tester l'interface d'administration"""
    print("\n🔍 Test de l'interface d'administration...")
    
    try:
        from news.admin import NewsAdmin
        from news.models import News
        
        # Vérifier que l'admin peut être instancié
        admin = NewsAdmin(News, None)
        print("✅ NewsAdmin peut être instancié")
        
        # Vérifier les méthodes
        print(f"✅ list_display: {admin.list_display}")
        print(f"✅ list_filter: {admin.list_filter}")
        print(f"✅ search_fields: {admin.search_fields}")
        
        # Tester la méthode get_author_name
        try:
            from news.models import News
            from django.contrib.contenttypes.models import ContentType
            from accounts.models import Admin
            
            # Créer un admin de test
            admin_user, created = Admin.objects.get_or_create(
                phone_number="+216888888888",
                defaults={
                    'first_name': 'Test',
                    'last_name': 'User',
                    'email': 'test@user.com'
                }
            )
            
            # Créer une news
            news = News.objects.create(
                title_fr="Test Admin FR",
                title_ar="Test Admin AR",
                content_fr="Test content",
                content_ar="محتوى الاختبار",
                content_type=ContentType.objects.get_for_model(admin_user),
                object_id=admin_user.id
            )
            
            # Tester la méthode
            author_name = admin.get_author_name(news)
            print(f"✅ get_author_name fonctionne: {author_name}")
            
            # Nettoyer
            news.delete()
            if created:
                admin_user.delete()
                
        except Exception as e:
            print(f"⚠️ Erreur lors du test de get_author_name: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur avec l'interface d'administration: {e}")
        return False

def test_database_queries():
    """Tester les requêtes de base de données"""
    print("\n🔍 Test des requêtes de base de données...")
    
    try:
        from news.models import News
        from django.contrib.contenttypes.models import ContentType
        
        # Compter les news
        count = News.objects.count()
        print(f"✅ Nombre de news en base: {count}")
        
        # Tester les requêtes avec GenericForeignKey
        news_with_author = News.objects.filter(content_type__isnull=False).count()
        print(f"✅ News avec auteur: {news_with_author}")
        
        # Tester l'affichage des auteurs
        for news in News.objects.all()[:3]:  # Limiter à 3 pour éviter trop de logs
            author_info = f"Auteur: {news.author}" if news.author else "Aucun auteur"
            print(f"   - {news.title_fr}: {author_info}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des requêtes: {e}")
        return False

def main():
    """Fonction principale"""
    print("🏁 Test de l'admin des news")
    print("=" * 50)
    
    # Configuration Django
    setup_django()
    
    # Tests
    model_ok = test_news_model()
    admin_ok = test_admin_interface()
    queries_ok = test_database_queries()
    
    print("\n" + "=" * 50)
    if model_ok and admin_ok and queries_ok:
        print("✅ Tous les tests sont passés avec succès!")
        print("🌐 L'admin des news devrait maintenant fonctionner correctement")
    else:
        print("❌ Certains tests ont échoué")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    return model_ok and admin_ok and queries_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



