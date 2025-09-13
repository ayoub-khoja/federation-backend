#!/usr/bin/env python3
"""
Script de correction rapide pour les problèmes de connexion mobile
"""

import os
import sys
import socket
import subprocess
import platform

def get_local_ip():
    """Obtenir l'adresse IP locale"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def fix_django_settings():
    """Corriger les paramètres Django pour l'accès mobile"""
    print("🔧 Correction des paramètres Django...")
    
    settings_file = "arbitrage_project/settings.py"
    
    try:
        # Lire le fichier settings
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier et corriger ALLOWED_HOSTS
        if "ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '192.168.1.101', '*']" in content:
            print("✅ ALLOWED_HOSTS déjà configuré correctement")
        else:
            # Remplacer la ligne ALLOWED_HOSTS
            import re
            pattern = r"ALLOWED_HOSTS = \[.*?\]"
            replacement = "ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '192.168.1.101', '*']"
            
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                
                # Écrire le fichier modifié
                with open(settings_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("✅ ALLOWED_HOSTS corrigé")
            else:
                print("⚠️ ALLOWED_HOSTS non trouvé, ajout manuel nécessaire")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction des paramètres: {e}")
        return False

def start_server_mobile():
    """Démarrer le serveur pour l'accès mobile"""
    print("🚀 Démarrage du serveur pour mobile...")
    
    ip = get_local_ip()
    
    print(f"🌐 Adresse IP locale: {ip}")
    print(f"🔗 URL pour mobile: http://{ip}:8000")
    
    print("\n📱 Instructions:")
    print("1. Ouvrez le navigateur de votre téléphone")
    print(f"2. Tapez: http://{ip}:8000")
    print("3. Vérifiez que la page se charge")
    
    print("\n🔧 Si ça ne marche pas:")
    print("1. Vérifiez que le téléphone et l'ordinateur sont sur le même WiFi")
    print("2. Désactivez temporairement le pare-feu")
    print("3. Redémarrez le routeur")
    
    try:
        # Démarrer le serveur
        cmd = [sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000']
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")

def test_connection():
    """Tester la connexion"""
    print("🔍 Test de connexion...")
    
    ip = get_local_ip()
    
    try:
        import requests
        
        # Test local
        try:
            response = requests.get("http://localhost:8000/api/", timeout=5)
            print("✅ Serveur accessible en local")
        except:
            print("❌ Serveur non accessible en local")
            return False
        
        # Test avec l'IP locale
        try:
            response = requests.get(f"http://{ip}:8000/api/", timeout=5)
            print(f"✅ Serveur accessible via IP locale: {ip}")
        except:
            print(f"❌ Serveur non accessible via IP locale: {ip}")
            return False
        
        return True
        
    except ImportError:
        print("⚠️ Module requests non disponible, test manuel nécessaire")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale"""
    print("🏁 Correction des problèmes de connexion mobile")
    print("=" * 60)
    
    # Changer vers le dossier backend
    os.chdir('backend')
    
    # Correction des paramètres
    fix_django_settings()
    
    # Test de connexion
    test_connection()
    
    # Démarrage du serveur
    start_server_mobile()

if __name__ == "__main__":
    main()


