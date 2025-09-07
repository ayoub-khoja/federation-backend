"""
Configuration Django pour la PRODUCTION (Render)
"""

from .settings import *
import os
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Hosts autorisés en production
ALLOWED_HOSTS = [
    'federation-backend.onrender.com',
    'localhost',
    '127.0.0.1',
]

# Configuration de la base de données PostgreSQL (Render)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='arbitrage_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'options': '-c search_path=arbitrage_app,public'
        },
        'CONN_MAX_AGE': 600,
    }
}

# CORS Configuration pour la production
CORS_ALLOWED_ORIGINS = [
    "https://federation-backend.onrender.com",
    "https://federation-admin-front.vercel.app",
    "https://federation-mobile-front.vercel.app",
    "https://federation-mobile.vercel.app",  # URL mobile corrigée
]

# Permettre temporairement toutes les origines pour le débogage
CORS_ALLOW_ALL_ORIGINS = True  # Temporaire pour le débogage

# Configuration des fichiers statiques pour la production
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configuration des médias pour la production
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuration VAPID pour la production
VAPID_PRIVATE_KEY = config('VAPID_PRIVATE_KEY', default='your_production_vapid_private_key')
VAPID_PUBLIC_KEY = config('VAPID_PUBLIC_KEY', default='your_production_vapid_public_key')
VAPID_EMAIL = config('VAPID_EMAIL', default='admin@arbitrage.tn')

# URLs de production
PRODUCTION_URL = 'https://federation-backend.onrender.com'
API_BASE_URL = 'https://federation-backend.onrender.com/api'

# Sécurité renforcée pour la production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Configuration des sessions
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Configuration de logging pour le débogage
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Message de démarrage personnalisé
print("🚀 Serveur Django démarré en mode PRODUCTION")
print(f"🌐 URL du serveur: {PRODUCTION_URL}")
print(f"📱 API Base URL: {API_BASE_URL}")
print(f"🔒 DEBUG: {DEBUG}")
print(f"🌍 ALLOWED_HOSTS: {ALLOWED_HOSTS}")
print(f"🔗 CORS_ALLOW_ALL_ORIGINS: {CORS_ALLOW_ALL_ORIGINS}")
