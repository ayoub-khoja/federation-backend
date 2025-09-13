#!/usr/bin/env python3
"""
Script de diagnostic pour les problèmes de connexion mobile
"""

import os
import sys
import socket
import subprocess
import platform
import requests
from datetime import datetime

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

def check_server_running():
    """Vérifier si le serveur Django est en cours d'exécution"""
    print("🔍 Vérification du serveur Django...")
    
    try:
        response = requests.get("http://localhost:8000/api/accounts/arbitres/login/", timeout=5)
        if response.status_code in [200, 405, 400]:  # 405 = Method Not Allowed, 400 = Bad Request (normal pour GET sur POST endpoint)
            print("✅ Serveur Django fonctionne sur localhost:8000")
            return True
        else:
            print(f"⚠️ Serveur répond avec le code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Serveur Django non accessible sur localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def check_network_interface():
    """Vérifier les interfaces réseau"""
    print("\n🔍 Vérification des interfaces réseau...")
    
    try:
        import netifaces
        
        interfaces = netifaces.interfaces()
        print(f"📡 Interfaces réseau trouvées: {len(interfaces)}")
        
        for interface in interfaces:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip = addr['addr']
                    if not ip.startswith('127.'):
                        print(f"   - {interface}: {ip}")
        
        return True
    except ImportError:
        print("⚠️ Module netifaces non installé, utilisation de la méthode alternative")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des interfaces: {e}")
        return False

def check_firewall():
    """Vérifier les paramètres du pare-feu"""
    print("\n🔍 Vérification du pare-feu...")
    
    system = platform.system().lower()
    
    if system == "windows":
        print("🪟 Système Windows détecté")
        print("💡 Vérifiez les paramètres du Pare-feu Windows:")
        print("   1. Ouvrez 'Pare-feu Windows Defender'")
        print("   2. Cliquez sur 'Paramètres avancés'")
        print("   3. Vérifiez que le port 8000 est autorisé")
        print("   4. Ou désactivez temporairement le pare-feu pour tester")
        
    elif system == "darwin":  # macOS
        print("🍎 Système macOS détecté")
        print("💡 Vérifiez les paramètres du pare-feu:")
        print("   1. Préférences Système > Sécurité et confidentialité > Pare-feu")
        print("   2. Autorisez Python ou Django")
        
    else:  # Linux
        print("🐧 Système Linux détecté")
        print("💡 Vérifiez les paramètres du pare-feu:")
        print("   sudo ufw status")
        print("   sudo ufw allow 8000")
    
    return True

def test_mobile_connection():
    """Tester la connexion depuis le mobile"""
    print("\n📱 Test de connexion mobile...")
    
    ip = get_local_ip()
    test_urls = [
        f"http://{ip}:8000/",
        f"http://{ip}:8000/api/",
        f"http://{ip}:8000/api/accounts/arbitres/login/",
    ]
    
    print(f"🌐 Adresse IP locale: {ip}")
    print("🔗 URLs à tester sur votre téléphone:")
    
    for url in test_urls:
        print(f"   - {url}")
    
    print("\n📋 Instructions pour le test:")
    print("1. Ouvrez le navigateur de votre téléphone")
    print("2. Tapez l'une des URLs ci-dessus")
    print("3. Vérifiez si la page se charge")
    
    return ip

def check_django_settings():
    """Vérifier les paramètres Django"""
    print("\n🔍 Vérification des paramètres Django...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
        import django
        django.setup()
        
        from django.conf import settings
        
        print(f"✅ DEBUG: {settings.DEBUG}")
        print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
        
        if '*' in settings.ALLOWED_HOSTS:
            print("✅ Tous les hosts sont autorisés")
        else:
            print("⚠️ Vérifiez que votre IP est dans ALLOWED_HOSTS")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des paramètres: {e}")
        return False

def start_server_with_debug():
    """Démarrer le serveur avec des informations de debug"""
    print("\n🚀 Démarrage du serveur avec debug...")
    
    ip = get_local_ip()
    
    print(f"🌐 Serveur accessible sur:")
    print(f"   - http://localhost:8000")
    print(f"   - http://127.0.0.1:8000")
    print(f"   - http://{ip}:8000")
    
    print("\n📱 Pour tester sur mobile:")
    print(f"   Ouvrez: http://{ip}:8000")
    
    print("\n🔧 Commandes de démarrage:")
    print("   cd backend")
    print("   python manage.py runserver 0.0.0.0:8000")
    
    return ip

def provide_solutions():
    """Fournir des solutions aux problèmes courants"""
    print("\n💡 Solutions aux problèmes courants:")
    print("=" * 50)
    
    print("\n1. 🔧 Problème de pare-feu:")
    print("   - Désactivez temporairement le pare-feu")
    print("   - Autorisez le port 8000")
    print("   - Redémarrez le serveur")
    
    print("\n2. 🌐 Problème de réseau:")
    print("   - Vérifiez que le téléphone et l'ordinateur sont sur le même WiFi")
    print("   - Redémarrez le routeur si nécessaire")
    print("   - Essayez de partager la connexion mobile")
    
    print("\n3. 🔄 Problème de serveur:")
    print("   - Redémarrez le serveur Django")
    print("   - Vérifiez les logs d'erreur")
    print("   - Testez d'abord sur localhost")
    
    print("\n4. 📱 Problème d'application mobile:")
    print("   - Vérifiez l'URL configurée dans l'app")
    print("   - Testez l'URL dans le navigateur du téléphone")
    print("   - Vérifiez les paramètres de l'application")
    
    print("\n5. 🔍 Test de connectivité:")
    print("   - Ping depuis le téléphone vers l'ordinateur")
    print("   - Test de port avec une app de réseau")
    print("   - Vérification des logs du serveur")

def main():
    """Fonction principale"""
    print("🏁 Diagnostic des problèmes de connexion mobile")
    print("=" * 60)
    print(f"🕐 Diagnostic démarré à: {datetime.now()}")
    
    # Vérifications
    server_ok = check_server_running()
    network_ok = check_network_interface()
    settings_ok = check_django_settings()
    
    # Test de connexion mobile
    ip = test_mobile_connection()
    
    # Vérification du pare-feu
    check_firewall()
    
    # Solutions
    provide_solutions()
    
    # Démarrage du serveur
    start_server_with_debug()
    
    print("\n" + "=" * 60)
    print("🏁 Diagnostic terminé")
    
    if server_ok and settings_ok:
        print("✅ Le serveur semble correctement configuré")
        print("🔧 Le problème est probablement lié au réseau ou au pare-feu")
    else:
        print("❌ Le serveur a des problèmes de configuration")
        print("🔧 Corrigez les problèmes identifiés ci-dessus")

if __name__ == "__main__":
    main()


