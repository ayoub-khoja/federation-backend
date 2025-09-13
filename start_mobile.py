#!/usr/bin/env python3
"""
Script de démarrage pour l'application mobile
"""

import os
import sys
import subprocess
import socket
import platform

def get_local_ip():
    """Obtenir l'adresse IP locale"""
    try:
        # Se connecter à une adresse externe pour déterminer l'IP locale
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def start_backend():
    """Démarrer le serveur backend"""
    print("🚀 Démarrage du serveur backend...")
    
    try:
        # Changer vers le dossier backend
        os.chdir('backend')
        
        # Démarrer le serveur Django
        cmd = [sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000']
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur demandé")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du démarrage: {e}")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

def show_instructions():
    """Afficher les instructions pour l'application mobile"""
    ip = get_local_ip()
    
    print("📱 Instructions pour l'application mobile")
    print("=" * 50)
    print(f"🌐 Adresse IP locale: {ip}")
    print(f"🔗 URL du backend: http://{ip}:8000/api/")
    print()
    print("📋 Configuration de l'application mobile:")
    print(f"   - Backend URL: http://{ip}:8000/api/")
    print(f"   - Port: 8000")
    print()
    print("🔧 Si l'application ne se connecte pas:")
    print("   1. Vérifiez que le téléphone et l'ordinateur sont sur le même réseau WiFi")
    print("   2. Vérifiez que le port 8000 n'est pas bloqué par le pare-feu")
    print("   3. Testez l'URL dans le navigateur du téléphone:")
    print(f"      http://{ip}:8000/api/accounts/arbitres/login/")
    print()
    print("📱 Pour tester la connexion:")
    print(f"   Ouvrez http://{ip}:8000 dans le navigateur de votre téléphone")

def main():
    """Fonction principale"""
    print("🏁 Démarrage de l'application pour mobile")
    print("=" * 60)
    
    # Afficher les instructions
    show_instructions()
    
    print("\n" + "=" * 60)
    print("🚀 Démarrage du serveur...")
    print("   Appuyez sur Ctrl+C pour arrêter")
    print("=" * 60)
    
    # Démarrer le backend
    start_backend()

if __name__ == "__main__":
    main()


