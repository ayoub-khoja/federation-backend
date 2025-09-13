#!/usr/bin/env python3
"""
Script de démarrage mobile avec correction du pare-feu
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

def open_firewall_port():
    """Ouvrir le port 8000 dans le pare-feu Windows"""
    print("🔧 Ouverture du port 8000 dans le pare-feu...")
    
    try:
        # Commande pour ouvrir le port 8000
        cmd = [
            'netsh', 'advfirewall', 'firewall', 'add', 'rule',
            'name=Django Server Port 8000',
            'dir=in',
            'action=allow',
            'protocol=TCP',
            'localport=8000'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Port 8000 ouvert dans le pare-feu")
        else:
            print("⚠️ Impossible d'ouvrir le port automatiquement")
            print("💡 Ouvrez manuellement le Pare-feu Windows et autorisez le port 8000")
            
    except Exception as e:
        print(f"⚠️ Erreur lors de l'ouverture du port: {e}")

def start_server():
    """Démarrer le serveur Django"""
    ip = get_local_ip()
    
    print("🚀 Démarrage du serveur Django...")
    print(f"🌐 Adresse IP: {ip}")
    print(f"📱 URL pour mobile: http://{ip}:8000")
    print()
    print("📋 Instructions:")
    print("1. Ouvrez le navigateur de votre téléphone")
    print(f"2. Tapez: http://{ip}:8000")
    print("3. Si ça ne marche pas, désactivez temporairement le pare-feu Windows")
    print()
    print("🛑 Appuyez sur Ctrl+C pour arrêter le serveur")
    print("=" * 60)
    
    try:
        # Démarrer le serveur
        cmd = [sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000']
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Serveur arrêté")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Fonction principale"""
    print("🏁 Démarrage mobile avec correction du pare-feu")
    print("=" * 60)
    
    # Ouvrir le port dans le pare-feu
    open_firewall_port()
    
    # Démarrer le serveur
    start_server()

if __name__ == "__main__":
    main()
