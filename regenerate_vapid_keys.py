#!/usr/bin/env python3
"""
Régénération des clés VAPID pour résoudre les problèmes de validation
"""

import os
import sys
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

def generate_vapid_keys():
    """Générer de nouvelles clés VAPID"""
    
    print("🔑 RÉGÉNÉRATION DES CLÉS VAPID")
    print("=" * 50)
    
    try:
        # Générer une nouvelle paire de clés EC
        private_key = ec.generate_private_key(
            ec.SECP256R1(), 
            default_backend()
        )
        
        # Extraire la clé publique
        public_key = private_key.public_key()
        
        # Convertir en format PEM
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Convertir en format base64 pour VAPID
        private_b64 = base64.urlsafe_b64encode(
            private_pem.split(b'-----BEGIN PRIVATE KEY-----')[1]
            .split(b'-----END PRIVATE KEY-----')[0]
            .replace(b'\n', b'')
        ).decode('utf-8')
        
        public_b64 = base64.urlsafe_b64encode(
            public_pem.split(b'-----BEGIN PUBLIC KEY-----')[1]
            .split(b'-----END PUBLIC KEY-----')[0]
            .replace(b'\n', b'')
        ).decode('utf-8')
        
        print("✅ Nouvelles clés VAPID générées avec succès!")
        print(f"\n🔐 Clé privée VAPID:")
        print(f"   {private_b64}")
        print(f"\n🔓 Clé publique VAPID:")
        print(f"   {public_b64}")
        
        # Mettre à jour vapid_config.py
        update_vapid_config(private_b64, public_b64)
        
        return private_b64, public_b64
        
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        return None, None

def update_vapid_config(private_key, public_key):
    """Mettre à jour le fichier vapid_config.py"""
    
    print("\n📝 MISE À JOUR DE VAPID_CONFIG.PY")
    print("=" * 40)
    
    try:
        config_content = f'''#!/usr/bin/env python3
"""
Configuration VAPID pour les notifications push
"""

# Clés VAPID régénérées
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
        
        # Mettre à jour le frontend
        update_frontend_config(public_key)
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")

def update_frontend_config(public_key):
    """Mettre à jour la configuration frontend"""
    
    print("\n🌐 MISE À JOUR DU FRONTEND")
    print("=" * 35)
    
    try:
        frontend_path = "../frontend/src/config/environment.ts"
        
        if os.path.exists(frontend_path):
            with open(frontend_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remplacer la clé publique VAPID
            import re
            new_content = re.sub(
                r"PUBLIC_KEY: '[^']*'",
                f"PUBLIC_KEY: '{public_key}'",
                content
            )
            
            with open(frontend_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ environment.ts mis à jour")
        else:
            print("⚠️  Fichier frontend non trouvé")
            
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour frontend: {e}")

def verify_keys():
    """Vérifier que les nouvelles clés sont valides"""
    
    print("\n🔍 VÉRIFICATION DES NOUVELLES CLÉS")
    print("=" * 40)
    
    try:
        from vapid_config import VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY
        
        print(f"✅ Clé privée: {len(VAPID_PRIVATE_KEY)} caractères")
        print(f"✅ Clé publique: {len(VAPID_PUBLIC_KEY)} caractères")
        print(f"✅ Format privée: {VAPID_PRIVATE_KEY.startswith('MIGHAgEAMBMGByqGSM49')}")
        print(f"✅ Format publique: {VAPID_PUBLIC_KEY.startswith('MFkwEwYHKoZIzj0CAQYI')}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur import: {e}")
        return False

if __name__ == "__main__":
    print("🚀 RÉGÉNÉRATION DES CLÉS VAPID")
    print("=" * 50)
    
    # Générer de nouvelles clés
    private_key, public_key = generate_vapid_keys()
    
    if private_key and public_key:
        # Vérifier les nouvelles clés
        if verify_keys():
            print("\n" + "=" * 50)
            print("✅ RÉGÉNÉRATION TERMINÉE AVEC SUCCÈS!")
            print("\n💡 Prochaines étapes:")
            print("   1. Redémarrer le serveur Django")
            print("   2. Redémarrer le frontend")
            print("   3. Supprimer les anciens abonnements")
            print("   4. Créer de nouveaux abonnements")
            print("   5. Tester les notifications")
        else:
            print("❌ Vérification des clés échouée")
    else:
        print("❌ Génération des clés échouée")
    
    sys.exit(0 if private_key and public_key else 1)







