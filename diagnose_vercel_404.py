#!/usr/bin/env python3
"""
Script de diagnostic pour l'erreur 404 Vercel Mobile
"""

import requests
import json
import time
from datetime import datetime

def test_vercel_endpoints():
    """Tester les endpoints de l'application mobile Vercel"""
    
    base_url = "https://federation-mobile.vercel.app"
    
    endpoints_to_test = [
        "/",
        "/home",
        "/_next/static/chunks/app/home/page-0ea1266b44ec7aa6.js",
        "/_next/static/chunks/webpack.js",
        "/_next/static/css/app/layout.css",
        "/api/health",
        "/api/status"
    ]
    
    print("🔍 Diagnostic de l'application mobile Vercel")
    print("=" * 60)
    print(f"🌐 URL de base: {base_url}")
    print(f"🕐 Test démarré à: {datetime.now()}")
    print()
    
    results = {}
    
    for endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        print(f"🔗 Test: {url}")
        
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            
            status = response.status_code
            content_type = response.headers.get('content-type', 'Unknown')
            content_length = len(response.content)
            
            print(f"   Status: {status}")
            print(f"   Content-Type: {content_type}")
            print(f"   Content-Length: {content_length}")
            
            if status == 200:
                print("   ✅ OK")
            elif status == 404:
                print("   ❌ 404 - Fichier non trouvé")
            elif status == 500:
                print("   ❌ 500 - Erreur serveur")
            else:
                print(f"   ⚠️ Status inattendu: {status}")
            
            results[endpoint] = {
                'status': status,
                'content_type': content_type,
                'content_length': content_length,
                'success': status == 200
            }
            
        except requests.exceptions.Timeout:
            print("   ⏰ Timeout - Le serveur met trop de temps à répondre")
            results[endpoint] = {'status': 'timeout', 'success': False}
            
        except requests.exceptions.ConnectionError:
            print("   ❌ Erreur de connexion")
            results[endpoint] = {'status': 'connection_error', 'success': False}
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            results[endpoint] = {'status': 'error', 'error': str(e), 'success': False}
        
        print()
        time.sleep(1)  # Pause entre les requêtes
    
    return results

def analyze_results(results):
    """Analyser les résultats du diagnostic"""
    
    print("📊 Analyse des résultats")
    print("=" * 60)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results.values() if r.get('success', False))
    failed_tests = total_tests - successful_tests
    
    print(f"📈 Total des tests: {total_tests}")
    print(f"✅ Tests réussis: {successful_tests}")
    print(f"❌ Tests échoués: {failed_tests}")
    print()
    
    # Analyser les erreurs spécifiques
    js_errors = []
    css_errors = []
    page_errors = []
    
    for endpoint, result in results.items():
        if not result.get('success', False):
            if endpoint.endswith('.js'):
                js_errors.append(endpoint)
            elif endpoint.endswith('.css'):
                css_errors.append(endpoint)
            elif not endpoint.startswith('/_next/'):
                page_errors.append(endpoint)
    
    if js_errors:
        print("🔧 Erreurs JavaScript détectées:")
        for error in js_errors:
            print(f"   - {error}")
        print()
    
    if css_errors:
        print("🎨 Erreurs CSS détectées:")
        for error in css_errors:
            print(f"   - {error}")
        print()
    
    if page_errors:
        print("📄 Erreurs de pages détectées:")
        for error in page_errors:
            print(f"   - {error}")
        print()
    
    # Recommandations
    print("💡 Recommandations:")
    print("=" * 60)
    
    if js_errors or css_errors:
        print("1. 🔄 Forcer un nouveau build sur Vercel")
        print("   - Aller sur vercel.com")
        print("   - Sélectionner le projet federation-mobile")
        print("   - Cliquer sur 'Redeploy'")
        print()
    
    if page_errors:
        print("2. 🔍 Vérifier la configuration des routes")
        print("   - Vérifier le fichier next.config.js")
        print("   - Vérifier la structure des dossiers app/")
        print()
    
    print("3. 🧹 Nettoyer le cache Vercel")
    print("   - Aller dans Settings > Functions")
    print("   - Cliquer sur 'Clear Cache'")
    print()
    
    print("4. 📝 Vérifier les logs de build")
    print("   - Aller dans l'onglet 'Deployments'")
    print("   - Cliquer sur le dernier déploiement")
    print("   - Vérifier les logs de build")
    print()
    
    return {
        'total': total_tests,
        'successful': successful_tests,
        'failed': failed_tests,
        'js_errors': js_errors,
        'css_errors': css_errors,
        'page_errors': page_errors
    }

def test_backend_connectivity():
    """Tester la connectivité avec le backend"""
    
    print("🔗 Test de connectivité avec le backend")
    print("=" * 60)
    
    backend_urls = [
        "https://federation-backend.onrender.com/api/accounts/arbitre/login/",
        "https://federation-backend.onrender.com/api/news/",
        "https://federation-backend.onrender.com/admin/"
    ]
    
    for url in backend_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ {url} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - Erreur: {e}")

def main():
    """Fonction principale"""
    print("🏁 Diagnostic de l'erreur 404 Vercel Mobile")
    print("=" * 80)
    print()
    
    # Test des endpoints Vercel
    results = test_vercel_endpoints()
    
    # Analyse des résultats
    analysis = analyze_results(results)
    
    # Test de connectivité backend
    test_backend_connectivity()
    
    print("\n" + "=" * 80)
    print("🏁 Diagnostic terminé")
    
    if analysis['failed'] == 0:
        print("✅ Tous les tests sont passés - L'application fonctionne correctement")
    else:
        print(f"❌ {analysis['failed']} tests ont échoué - Action requise")
        print("🔧 Suivez les recommandations ci-dessus pour résoudre les problèmes")

if __name__ == "__main__":
    main()



