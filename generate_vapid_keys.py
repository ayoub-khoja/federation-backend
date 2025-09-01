#!/usr/bin/env python3
"""
Script pour générer les clés VAPID pour les notifications push
"""

from pywebpush import WebPushException, webpush
from py_vapid import Vapid
from cryptography.hazmat.primitives import serialization
import base64
import os

def generate_vapid_keys():
    """Génère une nouvelle paire de clés VAPID"""
    
    # Créer une instance VAPID
    vapid = Vapid()
    
    # Générer les clés
    vapid.generate_keys()
    private_key = vapid.private_key
    public_key = vapid.public_key
    
    # Convertir en base64 pour le stockage
    # Les clés sont des objets cryptographiques, il faut les convertir en bytes
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    private_key_b64 = base64.urlsafe_b64encode(private_key_bytes).decode('utf-8')
    public_key_b64 = base64.urlsafe_b64encode(public_key_bytes).decode('utf-8')
    
    print("🔑 Clés VAPID générées avec succès !")
    print()
    print("📝 Ajoutez ces variables dans votre fichier .env :")
    print()
    print(f"VAPID_PRIVATE_KEY={private_key_b64}")
    print(f"VAPID_PUBLIC_KEY={public_key_b64}")
    print()
    print("📱 Et dans votre fichier .env.local du frontend :")
    print()
    print(f"NEXT_PUBLIC_VAPID_PUBLIC_KEY={public_key_b64}")
    print()
    print("⚠️  IMPORTANT : Ne partagez JAMAIS la clé privée !")
    print("✅ La clé publique peut être partagée librement.")
    
    return private_key_b64, public_key_b64

if __name__ == "__main__":
    generate_vapid_keys()
