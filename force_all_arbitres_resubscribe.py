#!/usr/bin/env python3
"""
Script pour forcer tous les arbitres à se réabonner aux notifications push
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')
django.setup()

from accounts.models import Arbitre, PushSubscription
from django.utils import timezone

def force_all_arbitres_resubscribe():
    """Forcer tous les arbitres à se réabonner"""
    
    print("🔄 FORÇAGE DU RÉABONNEMENT POUR TOUS LES ARBITRES")
    print("=" * 60)
    
    # 1. Supprimer TOUS les abonnements existants
    print("\n🗑️ SUPPRESSION DE TOUS LES ABONNEMENTS EXISTANTS")
    
    total_existing = PushSubscription.objects.count()
    if total_existing > 0:
        PushSubscription.objects.all().delete()
        print(f"✅ {total_existing} abonnements supprimés")
    else:
        print("ℹ️  Aucun abonnement existant à supprimer")
    
    # 2. Lister tous les arbitres actifs
    print("\n👥 LISTE DE TOUS LES ARBITRES ACTIFS")
    
    arbitres = Arbitre.objects.filter(is_active=True)
    total_arbitres = arbitres.count()
    
    print(f"📊 Total arbitres actifs: {total_arbitres}")
    
    for i, arbitre in enumerate(arbitres, 1):
        print(f"  {i:2d}. {arbitre.get_full_name()} (ID: {arbitre.id})")
    
    # 3. Instructions pour le réabonnement
    print("\n📋 INSTRUCTIONS POUR LE RÉABONNEMENT")
    print("=" * 50)
    
    print("🚨 IMPORTANT : Tous les arbitres doivent maintenant se réabonner !")
    print("\n📱 ÉTAPES POUR CHAQUE ARBITRE :")
    print("   1. Se connecter à l'application frontend")
    print("   2. Aller dans les paramètres de notifications")
    print("   3. Désactiver les notifications (bouton OFF)")
    print("   4. Réactiver les notifications (bouton ON)")
    print("   5. Accepter la demande de permission du navigateur")
    
    print("\n🔄 ALTERNATIVE RAPIDE (Console navigateur) :")
    print("   Exécuter ce code dans la console :")
    
    console_code = """
// Code à exécuter dans la console du navigateur
console.log('🔄 Forçage de la réinscription...');

// 1. Désenregistrer le service worker
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(function(registrations) {
        for(let registration of registrations) {
            registration.unregister();
            console.log('✅ Service Worker désenregistré');
        }
    });
}

// 2. Vider le cache
if ('caches' in window) {
    caches.keys().then(function(names) {
        for (let name of names) {
            caches.delete(name);
            console.log('🗑️ Cache supprimé:', name);
        }
    });
}

// 3. Redémarrer la page
console.log('🔄 Redémarrage dans 3 secondes...');
setTimeout(() => {
    window.location.reload();
}, 3000);
"""
    
    print(console_code)
    
    # 4. Vérification finale
    print("\n🔍 VÉRIFICATION FINALE")
    print("Après le réabonnement, vérifiez avec :")
    print("   python check_subscription.py")
    
    # 5. Créer un fichier de guide
    guide_content = f"""# GUIDE DE RÉABONNEMENT AUX NOTIFICATIONS PUSH

## 🚨 SITUATION ACTUELLE
- Tous les abonnements ont été supprimés
- {total_arbitres} arbitres actifs sans abonnements
- Les notifications ne fonctionneront plus jusqu'au réabonnement

## 📱 ÉTAPES POUR CHAQUE ARBITRE

### Option 1 : Interface utilisateur
1. Se connecter à l'application frontend
2. Aller dans les paramètres de notifications
3. Désactiver les notifications (bouton OFF)
4. Réactiver les notifications (bouton ON)
5. Accepter la demande de permission du navigateur

### Option 2 : Console du navigateur
1. Ouvrir la console du navigateur (F12)
2. Exécuter le code JavaScript fourni
3. Attendre le redémarrage automatique
4. Réactiver les notifications

## ✅ VÉRIFICATION
Après le réabonnement, vérifiez avec :
```bash
python check_subscription.py
```

## 🎯 OBJECTIF
Tous les arbitres doivent avoir des abonnements actifs pour recevoir les notifications automatiques lors des désignations.

Date de création : {timezone.now().strftime('%d/%m/%Y %H:%M')}
"""
    
    guide_file = "GUIDE_REABONNEMENT.md"
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"\n📖 Guide créé : {guide_file}")
    
    return True

if __name__ == "__main__":
    success = force_all_arbitres_resubscribe()
    sys.exit(0 if success else 1)
