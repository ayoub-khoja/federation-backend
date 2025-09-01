#!/usr/bin/env python3
"""
Script pour forcer la mise à jour complète des clés VAPID
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

def force_vapid_update():
    """Forcer la mise à jour complète des clés VAPID"""
    
    print("🚀 FORCE UPDATE COMPLET DES CLÉS VAPID")
    print("=" * 60)
    
    # 1. Supprimer TOUS les abonnements existants
    print("\n🗑️  SUPPRESSION FORCÉE DE TOUS LES ABONNEMENTS")
    
    total_subscriptions = PushSubscription.objects.count()
    if total_subscriptions > 0:
        print(f"  📱 Suppression de {total_subscriptions} abonnements...")
        
        # Supprimer tous les abonnements sans demander
        PushSubscription.objects.all().delete()
        print("  ✅ Tous les abonnements supprimés")
    else:
        print("  ✅ Aucun abonnement à supprimer")
    
    # 2. Générer de NOUVELLES clés VAPID (différentes des précédentes)
    print("\n🔑 GÉNÉRATION DE NOUVELLES CLÉS VAPID")
    
    # Générer une nouvelle paire de clés EC
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()
    
    # Convertir en format base64 URL-safe
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Extraire la clé publique brute et la convertir en base64
    public_raw = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )
    
    private_b64 = base64.urlsafe_b64encode(private_pem).decode('utf-8').rstrip('=')
    public_b64 = base64.urlsafe_b64encode(public_raw).decode('utf-8').rstrip('=')
    
    print(f"  ✅ Nouvelles clés VAPID générées!")
    print(f"  🔐 Clé privée: {len(private_b64)} caractères")
    print(f"  🔓 Clé publique: {len(public_b64)} caractères")
    
    # 3. Mettre à jour vapid_config.py
    print("\n📝 MISE À JOUR FORCÉE DE VAPID_CONFIG.PY")
    
    config_content = f'''#!/usr/bin/env python3
"""
Configuration VAPID pour les notifications push - MISE À JOUR FORCÉE
"""

# Clés VAPID NOUVELLES générées automatiquement
VAPID_PRIVATE_KEY = "{private_b64}"
VAPID_PUBLIC_KEY = "{public_b64}"
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
    
    print("✅ vapid_config.py mis à jour avec FORCE")
    
    # 4. Mettre à jour la configuration frontend
    print("\n🌐 MISE À JOUR FORCÉE DU FRONTEND")
    
    frontend_config = '../frontend/src/config/environment.ts'
    
    try:
        with open(frontend_config, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer la clé publique VAPID
        import re
        old_key_pattern = r"PUBLIC_KEY: '[^']*'"
        new_key_line = f"PUBLIC_KEY: '{public_b64}'"
        
        if old_key_pattern in content:
            content = re.sub(old_key_pattern, new_key_line, content)
            
            with open(frontend_config, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Configuration frontend mise à jour avec FORCE")
        else:
            print("  ⚠️  Clé publique VAPID non trouvée dans la configuration frontend")
            
    except Exception as e:
        print(f"  ❌ Erreur lors de la mise à jour frontend: {e}")
    
    # 5. Mettre à jour le service worker
    print("\n🔧 MISE À JOUR DU SERVICE WORKER")
    
    sw_file = '../frontend/public/sw.js'
    
    try:
        with open(sw_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ajouter un commentaire de mise à jour
        update_comment = f'''
// ============================================================================
// MISE À JOUR FORCÉE VAPID - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
// Nouvelle clé publique: {public_b64[:20]}...
// ============================================================================
'''
        
        # Ajouter au début du fichier
        content = update_comment + content
        
        with open(sw_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Service worker mis à jour avec timestamp")
        
    except Exception as e:
        print(f"  ❌ Erreur lors de la mise à jour du service worker: {e}")
    
    # 6. Instructions pour l'utilisateur
    print("\n🚨 INSTRUCTIONS CRITIQUES POUR L'UTILISATEUR")
    print("=" * 60)
    print("1. ARRÊTER le serveur Django (Ctrl+C)")
    print("2. VIDER le cache du navigateur (Ctrl+Shift+Delete)")
    print("3. FERMER complètement le navigateur")
    print("4. RELANCER le serveur Django: python manage.py runserver")
    print("5. REOUVRIR le navigateur et aller sur l'application")
    print("6. ACCEPTER les notifications push à nouveau")
    print("7. Les nouvelles clés VAPID seront utilisées")
    
    print(f"\n🔑 NOUVELLES CLÉS VAPID:")
    print(f"  🔐 Privée: {private_b64}")
    print(f"  🔓 Publique: {public_b64}")
    
    print("\n⚠️  ATTENTION: Les anciens abonnements ne fonctionneront plus!")
    print("   Les utilisateurs devront se réabonner aux notifications.")
    
    return True

if __name__ == "__main__":
    from django.utils import timezone
    success = force_vapid_update()
    sys.exit(0 if success else 1)
