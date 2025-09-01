// Script à exécuter dans la console du navigateur
// Pour forcer la réinscription aux notifications push

console.log('🔄 Forçage de la réinscription aux notifications push...');

// 1. Désenregistrer le service worker actuel
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
console.log('🔄 Redémarrage de la page dans 3 secondes...');
setTimeout(() => {
    window.location.reload();
}, 3000);

console.log('💡 Après le redémarrage, réactivez les notifications dans les paramètres');
