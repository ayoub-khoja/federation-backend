"""
Configuration des URLs des frontends
"""

# URLs des frontends en production
PRODUCTION_FRONTENDS = {
    'admin': 'https://federation-admin-front.vercel.app',
    'mobile': 'https://federation-mobile-front.vercel.app',
    'backend': 'https://federation-backend.onrender.com',
}

# URLs des frontends en développement local
LOCAL_FRONTENDS = {
    'admin': 'http://localhost:3000',
    'mobile': 'http://localhost:3001',
    'backend': 'http://localhost:8000',
}

# Configuration CORS pour tous les environnements
CORS_ALLOWED_ORIGINS = [
    # Local
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://192.168.1.101:3000",
    "http://192.168.1.101:3001",
    
    # Production Vercel
    "https://federation-admin-front.vercel.app",
    "https://federation-mobile-front.vercel.app",
    
    # Production Render
    "https://federation-backend.onrender.com",
]

# Configuration des redirections après login
LOGIN_REDIRECT_URLS = {
    'admin': 'https://federation-admin-front.vercel.app/dashboard',
    'mobile': 'https://federation-mobile-front.vercel.app/home',
}

# Configuration des notifications push
NOTIFICATION_CONFIG = {
    'admin_frontend': 'https://federation-admin-front.vercel.app',
    'mobile_frontend': 'https://federation-mobile-front.vercel.app',
    'backend_api': 'https://federation-backend.onrender.com/api',
}


