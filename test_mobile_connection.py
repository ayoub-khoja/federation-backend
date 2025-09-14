#!/usr/bin/env python3
"""
Test de connexion mobile
"""

import requests
import socket

def test_connection():
    """Tester la connexion mobile"""
    print("🔍 Test de connexion mobile...")
    
    # Obtenir l'IP locale
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = "192.168.1.100"
    
    print(f"🌐 IP locale: {ip}")
    
    # URLs à tester
    urls = [
        f"http://{ip}:8000/",
        f"http://{ip}:8000/api/",
        f"http://{ip}:8000/api/accounts/arbitres/login/"
    ]
    
    print("\n📱 Testez ces URLs sur votre téléphone:")
    for url in urls:
        print(f"   {url}")
    
    print("\n🔧 Si ça ne marche pas:")
    print("1. Désactivez temporairement le pare-feu Windows")
    print("2. Redémarrez le routeur")
    print("3. Vérifiez que le téléphone et l'ordinateur sont sur le même WiFi")
    
    # Test local
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"\n✅ Serveur local: OK (Status: {response.status_code})")
    except Exception as e:
        print(f"\n❌ Serveur local: Erreur ({e})")

if __name__ == "__main__":
    test_connection()



