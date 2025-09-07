#!/usr/bin/env python3
"""
Script pour corriger les auteurs des news existantes
"""

import os
import sys
import django
from django.conf import settings

def setup_django():
    """Configuration Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
    django.setup()

def fix_news_authors():
    """Corriger les auteurs des news existantes"""
    print("🔧 Correction des auteurs des news...")
    
    try:
        from news.models import News
        from django.contrib.contenttypes.models import ContentType
        from accounts.models import Admin
        
        # Compter les news sans auteur
        news_without_author = News.objects.filter(content_type__isnull=True)
        count = news_without_author.count()
        print(f"📊 News sans auteur: {count}")
        
        if count == 0:
            print("✅ Toutes les news ont déjà un auteur")
            return True
        
        # Créer un admin par défaut si nécessaire
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
        updated_count = 0
        for news in news_without_author:
            news.content_type = admin_content_type
            news.object_id = default_admin.id
            news.save()
            updated_count += 1
            print(f"   ✅ News '{news.title_fr}' assignée à {default_admin.get_full_name()}")
        
        print(f"🎉 {updated_count} news corrigées avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")
        return False

def verify_news_authors():
    """Vérifier que tous les auteurs sont correctement assignés"""
    print("\n🔍 Vérification des auteurs...")
    
    try:
        from news.models import News
        
        total_news = News.objects.count()
        news_with_author = News.objects.filter(content_type__isnull=False).count()
        news_without_author = total_news - news_with_author
        
        print(f"📊 Total des news: {total_news}")
        print(f"✅ News avec auteur: {news_with_author}")
        print(f"❌ News sans auteur: {news_without_author}")
        
        if news_without_author == 0:
            print("🎉 Toutes les news ont un auteur assigné!")
            return True
        else:
            print("⚠️ Il reste des news sans auteur")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def main():
    """Fonction principale"""
    print("🏁 Correction des auteurs des news")
    print("=" * 50)
    
    # Configuration Django
    setup_django()
    
    # Correction
    fix_ok = fix_news_authors()
    
    # Vérification
    verify_ok = verify_news_authors()
    
    print("\n" + "=" * 50)
    if fix_ok and verify_ok:
        print("✅ Correction terminée avec succès!")
        print("🌐 L'admin des news devrait maintenant fonctionner sans erreur 500")
    else:
        print("❌ La correction a échoué")
        print("🔧 Vérifiez les erreurs ci-dessus")
    
    return fix_ok and verify_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
