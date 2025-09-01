#!/usr/bin/env python3
"""
Script complet pour résoudre le problème VAPID et configurer les notifications push
"""

import os
import sys
import django
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import PushSubscription
from django.conf import settings

def generate_new_vapid_keys():
    """Générer de nouvelles clés VAPID valides"""
    print("🔑 GÉNÉRATION DE NOUVELLES CLÉS VAPID")
    
    # Générer une nouvelle paire de clés EC
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    
    # Convertir en format base64 URL-safe
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Extraire la clé publique brute et la convertir en base64
    public_raw = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )
    
    private_b64 = base64.urlsafe_b64encode(private_pem).decode('utf-8').rstrip('=')
    public_b64 = base64.urlsafe_b64encode(public_raw).decode('utf-8').rstrip('=')
    
    print(f"✅ Nouvelles clés VAPID générées!")
    print(f"  Clé privée: {len(private_b64)} caractères")
    print(f"  Clé publique: {len(public_b64)} caractères")
    
    return private_b64, public_b64

def update_vapid_config(private_key, public_key):
    """Mettre à jour le fichier vapid_config.py"""
    print("\n📝 MISE À JOUR DE VAPID_CONFIG.PY")
    
    config_content = f'''#!/usr/bin/env python3
"""
Configuration VAPID pour les notifications push
"""

# Clés VAPID fonctionnelles générées automatiquement
VAPID_PRIVATE_KEY = "{private_key}"
VAPID_PUBLIC_KEY = "{public_key}"
VAPID_EMAIL = "admin@arbitrage.tn"

# Configuration des notifications
NOTIFICATION_CONFIG = {{
    'default_icon': '/static/images/notification-icon.png',
    'default_badge': '/static/images/badge-icon.png',
    'default_tag': 'arbitrage',
    'require_interaction': True,
    'silent': False,
    'vibrate': [200, 100, 200],
    'actions': [
        {{
            'action': 'view',
            'title': 'Voir',
            'icon': '/static/images/view-icon.png'
        }},
        {{
            'action': 'dismiss',
            'title': 'Fermer'
        }}
    ]
}}

# Types de notifications supportés
NOTIFICATION_TYPES = {{
    'designation_created': {{
        'title': '🏆 Nouvelle Désignation d\\'Arbitrage',
        'icon': '/static/images/designation-icon.png',
        'tag': 'designation',
        'priority': 'high'
    }},
    'designation_updated': {{
        'title': '🔄 Désignation Mise à Jour',
        'icon': '/static/images/update-icon.png',
        'tag': 'designation_update',
        'priority': 'normal'
    }},
    'designation_cancelled': {{
        'title': '❌ Désignation Annulée',
        'icon': '/static/images/cancel-icon.png',
        'tag': 'designation_cancel',
        'priority': 'high'
    }},
    'match_reminder': {{
        'title': '⏰ Rappel de Match',
        'icon': '/static/images/reminder-icon.png',
        'tag': 'reminder',
        'priority': 'normal'
    }}
}}
'''
    
    with open('vapid_config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ vapid_config.py mis à jour")

def update_django_settings():
    """Ajouter les clés VAPID aux paramètres Django"""
    print("\n⚙️  MISE À JOUR DES PARAMÈTRES DJANGO")
    
    settings_file = 'arbitrage_project/settings.py'
    
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si les clés VAPID sont déjà présentes
        if 'VAPID_PRIVATE_KEY' in content:
            print("  ℹ️  Les clés VAPID sont déjà dans settings.py")
            return True
        
        # Ajouter les clés VAPID à la fin du fichier
        vapid_config = '''
# ============================================================================
# CONFIGURATION VAPID POUR LES NOTIFICATIONS PUSH
# ============================================================================

# Importer la configuration VAPID
try:
    from vapid_config import VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_EMAIL
except ImportError:
    # Valeurs par défaut si le fichier n'est pas trouvé
    VAPID_PRIVATE_KEY = "default_private_key"
    VAPID_PUBLIC_KEY = "default_public_key"
    VAPID_EMAIL = "admin@arbitrage.tn"
'''
        
        # Ajouter avant la dernière ligne
        if content.endswith('\n'):
            content += vapid_config
        else:
            content += '\n' + vapid_config
        
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Paramètres Django mis à jour avec les clés VAPID")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour de settings.py: {e}")
        return False

def update_frontend_config(public_key):
    """Mettre à jour la configuration frontend avec la nouvelle clé publique"""
    print("\n🌐 MISE À JOUR DE LA CONFIGURATION FRONTEND")
    
    frontend_config = f'frontend/src/config/environment.ts'
    
    try:
        with open(frontend_config, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer la clé publique VAPID
        old_key_pattern = r"PUBLIC_KEY: '[^']*'"
        new_key_line = f"PUBLIC_KEY: '{public_key}'"
        
        if old_key_pattern in content:
            import re
            content = re.sub(old_key_pattern, new_key_line, content)
            
            with open(frontend_config, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Configuration frontend mise à jour")
            return True
        else:
            print("  ℹ️  Clé publique VAPID non trouvée dans la configuration frontend")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour frontend: {e}")
        return False

def clean_old_subscriptions():
    """Nettoyer les anciens abonnements push"""
    print("\n🗑️  NETTOYAGE DES ANCIENS ABONNEMENTS")
    
    total_subscriptions = PushSubscription.objects.count()
    
    if total_subscriptions == 0:
        print("  ✅ Aucun abonnement à nettoyer")
        return True
    
    print(f"  📱 {total_subscriptions} abonnements trouvés")
    
    # Demander confirmation
    response = input(f"  ❓ Supprimer tous les abonnements ? (oui/non): ").lower().strip()
    if response not in ['oui', 'o', 'yes', 'y']:
        print("  ❌ Opération annulée")
        return False
    
    # Supprimer tous les abonnements
    deleted_count = 0
    for subscription in PushSubscription.objects.all():
        arbitre_name = subscription.arbitre.get_full_name()
        endpoint = subscription.endpoint[:30] + "..." if len(subscription.endpoint) > 30 else subscription.endpoint
        print(f"    Suppression: {arbitre_name} - {endpoint}")
        subscription.delete()
        deleted_count += 1
    
    print(f"  ✅ {deleted_count} abonnements supprimés")
    return True

def test_vapid_configuration():
    """Tester la configuration VAPID"""
    print("\n🧪 TEST DE LA CONFIGURATION VAPID")
    
    try:
        # Importer la configuration VAPID
        from vapid_config import VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_EMAIL
        
        print(f"  ✅ Clé privée: {len(VAPID_PRIVATE_KEY)} caractères")
        print(f"  ✅ Clé publique: {len(VAPID_PUBLIC_KEY)} caractères")
        print(f"  ✅ Email: {VAPID_EMAIL}")
        
        # Vérifier que les clés sont différentes
        if VAPID_PRIVATE_KEY != VAPID_PUBLIC_KEY:
            print("  ✅ Les clés privée et publique sont différentes")
            return True
        else:
            print("  ❌ Les clés privée et publique sont identiques")
            return False
            
    except ImportError as e:
        print(f"  ❌ Erreur d'import VAPID: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erreur lors du test: {e}")
        return False

def fix_vapid_issue():
    """Résoudre complètement le problème VAPID"""
    
    print("🔧 RÉSOLUTION COMPLÈTE DU PROBLÈME VAPID")
    print("=" * 60)
    
    # 1. Générer de nouvelles clés VAPID
    private_key, public_key = generate_new_vapid_keys()
    
    # 2. Mettre à jour la configuration VAPID
    update_vapid_config(private_key, public_key)
    
    # 3. Mettre à jour les paramètres Django
    if not update_django_settings():
        print("⚠️  Impossible de mettre à jour settings.py, continuons...")
    
    # 4. Mettre à jour la configuration frontend
    update_frontend_config(public_key)
    
    # 5. Nettoyer les anciens abonnements
    clean_old_subscriptions()
    
    # 6. Tester la configuration
    if test_vapid_configuration():
        print("\n🎯 PROBLÈME VAPID RÉSOLU!")
        print("\n💡 PROCHAINES ÉTAPES:")
        print("  1. Redémarrer le serveur Django")
        print("  2. Les utilisateurs devront se reconnecter")
        print("  3. Accepter les notifications push à nouveau")
        print("  4. Les notifications fonctionneront avec les nouvelles clés")
        print("\n🔑 NOUVELLES CLÉS VAPID:")
        print(f"  Privée: {private_key}")
        print(f"  Publique: {public_key}")
        return True
    else:
        print("\n❌ La configuration VAPID n'est pas correcte")
        return False

if __name__ == "__main__":
    success = fix_vapid_issue()
    sys.exit(0 if success else 1)

