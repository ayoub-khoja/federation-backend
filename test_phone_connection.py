#!/usr/bin/env python3
"""
Test de connexion téléphone
"""

import socket
import requests

def get_local_ip():
    """Obtenir l'IP locale"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.1.100"

def test_server():
    """Tester le serveur"""
    print("🔍 Test du serveur Django...")
    
    try:
        # Test local
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ Serveur local: OK (Status: {response.status_code})")
        
        # Test avec IP
        ip = get_local_ip()
        response = requests.get(f"http://{ip}:8000/", timeout=5)
        print(f"✅ Serveur IP: OK (Status: {response.status_code})")
        
        return True
    except Exception as e:
        print(f"❌ Erreur serveur: {e}")
        return False

def show_phone_instructions():
    """Afficher les instructions pour le téléphone"""
    ip = get_local_ip()
    
    print("\n📱 Instructions pour votre téléphone:")
    print("=" * 50)
    print(f"🌐 Adresse IP: {ip}")
    print(f"🔗 URL à tester: http://{ip}:8000")
    print()
    print("📋 Étapes:")
    print("1. Ouvrez le navigateur de votre téléphone")
    print(f"2. Tapez: http://{ip}:8000")
    print("3. Appuyez sur Entrée")
    print()
    print("🔧 Si ça ne marche pas:")
    print("1. Vérifiez que le téléphone et l'ordinateur sont sur le même WiFi")
    print("2. Désactivez temporairement le pare-feu Windows")
    print("3. Redémarrez le routeur")
    print("4. Essayez de partager la connexion mobile")

def main():
    """Fonction principale"""
    print("🏁 Test de connexion téléphone")
    print("=" * 50)
    
    # Test du serveur
    if test_server():
        show_phone_instructions()
    else:
        print("❌ Le serveur ne fonctionne pas")

if __name__ == "__main__":
    main()

