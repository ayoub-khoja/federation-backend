"""
Configuration Django pour le projet Direction Nationale de l'Arbitrage
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-8k2m9n0p1q2r3s4t5u6v7w8x9y0z1a2b3c4d5e6f7g8h9i0j1k2l3m4n5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '192.168.1.101', '*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    
    # Local apps
    'accounts',
    'matches',
    'news',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise pour servir les fichiers statiques
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'accounts.middleware.CustomJWTAuthenticationMiddleware',  # Activé pour l'authentification JWT
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'arbitrage_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'arbitrage_project.wsgi.application'

# Database
# Configuration PostgreSQL (commentée temporairement pour le développement local)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'federation_lookwashmy',
#         'USER': 'federation_lookwashmy',
#         'PASSWORD': 'e4da5358b37630b0bffebc73307975b96139252b',
#         'HOST': 'a3ch9u.h.filess.io',
#         'PORT': '61007',
#         'OPTIONS': {
#             'sslmode': 'disable',
#             'client_encoding': 'UTF8',
#         },
#     }
# }

# Configuration SQLite pour le développement local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Tunis'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configuration supplémentaire pour Django 5.x
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Configuration pour servir les fichiers statiques en développement
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configuration WhiteNoise
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Backend d'authentification personnalisé pour gérer les trois types d'utilisateurs
AUTHENTICATION_BACKENDS = [
    'accounts.authentication.MultiUserBackend',  # Activé pour l'authentification multi-utilisateurs
    'django.contrib.auth.backends.ModelBackend',
]

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'accounts.authentication.CustomJWTAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS Configuration
try:
    from frontend_config import CORS_ALLOWED_ORIGINS
except ImportError:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://192.168.1.101:3000",
        "http://192.168.1.101:3001",
        "https://federation-admin-front.vercel.app",
        "https://federation-mobile-front.vercel.app",
    ]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True  # Temporairement pour les tests

# Headers CORS additionnels
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# ============================================================================
# CONFIGURATION VAPID POUR LES NOTIFICATIONS PUSH
# ============================================================================

# Importer la configuration VAPID
try:
    from vapid_config import VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_EMAIL
except ImportError:
    # Valeurs par défaut si le fichier n'est pas trouvé
    VAPID_PRIVATE_KEY = "default_private_key"
    VAPID_PUBLIC_KEY = "default_public_key"
    VAPID_EMAIL = "admin@arbitrage.tn"

# ============================================================================
# CONFIGURATION FIREBASE CLOUD MESSAGING (FCM)
# ============================================================================

# Chemin vers le fichier de clé de service Firebase
# Remplacez par le chemin vers votre fichier firebase-service-account-key.json
FIREBASE_SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, 'firebase-service-account-key.json')

# Configuration Firebase alternative (variables d'environnement)
# Utilisez cette méthode si vous préférez stocker les clés dans les variables d'environnement
FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": "federation-16c7a",  # Votre Project ID réel
    "private_key_id": "a102a76da2a592bcaaccae5906e0434b4acd04cc",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCERDnFKxeOMdby\ntrL8UPriijZxvoXCFR6bOfylFgTgJVpRDQ3tUNv1/jXzW2ZuSDqp1vkTnGV+GnjE\nhdTprJrkkONczZzRyFmqMRQs8bDAtzF37acdkfkZniekGYu/Z0cHD0JXEPudHztI\n33ly2pVqtOarevrHmZcIXGwReqp98x9MU339eCNvT3ogMqyeJTowHKOJS6vOOM2G\nbM59s+pmdvDbVlZy/07donoyffs/fupgMfEhaB6Dj6dpaBisZ5sB/oOTJ1EVTfHB\nhC2KzdmjZ5ZRhL/j1oGam7a13IAb8VOY4jQssaMyG5tUCZNLjo2gXcqG06kTiScC\njZE3avy7AgMBAAECggEACbsROvm8Hmh5RVr+mQSGKKN9dOnM4mX2XfoqpaSUkD7/\nQYZB14tC23qr0m8Pfp6Ovk8D/Rbc+qWM6/ximRxrOtST/ZBc8KwaOKSqtNHFLLBt\nkcKosEq8dk+F4BNHDjpVZeYP/eLQeBNDo81ZHIOLSZHshIIkMAoTK/jMtI5/O4vL\n1qIFqNcnrWcCxLIo1mQlJiaSxlldVJZLkf3JGQ1+Z6gbxdSFmJokYuebcw69Dqwv\nKA91p1RB/47CdA1RVJJXHcLbT/3Qbgn9YiCGeWXqL5y9kglAEg3Y/RTwmf+cbfxP\nqK9LMotsrHLOQUMQ46WhFRAUjMwRP/7U9ce7RT4YtQKBgQC5av/FUwUtUKxmjL/h\nCnw0qUjtb/N/mxM9Rg8nVipsPjJ1RWEJ9jiZJaWcuhfcGWquQRMf27Nw8arGvz91\n/2pOM6NeXTK/RGtmxjhmIyrII/snJt14LR6ZJQ1pp7LIlqmW5T5G1v+fLZ4bJ6CX\n4mZs1WNMAcbJ6KVxpvpY2dFNpQKBgQC2nZxyWR3ZLfi8rJfND4892GV9L0rBqo1G\n9uOpSW8G5ZQu0BvSz/2jQ/lyvVVdK0UDHEzXBI/x8K6xa3BEfXyIj0euk7BRymKP\nb3lNjgEfYXtKkbHd9TdVwpMfeeHotV85ZZDfPxjFPSTtM5ZlslkR6ntndMv8jXT6\n6ClsuBvS3wKBgB61T+L4WvUkVUkuqmC1Adke6EsarXNG1ariPYRASwpeSrENaoLh\n2oHSsFkCoQz80KRHdslh85gTDjuYVQRP5uVIvBfWy57N0BPXZGPWEzHOc7wKPce3\ngUfP0SbcdUmvWir5kJTe6rsMLRFGQNymzFveA3IFIU0zUKNAClpIyNdZAoGAXmCK\nUBZ6dJlrqabRNStLbjz+BnqAeiJ4rSo/cmf/N2NC+AaZupO/k7c3nfL3wRTxr6/a\njm1PL0yiHBNYjC0GRVU3SKQPRdYApfyIhmpTbjJlE57Ee9+VX38VpfjJpgjGU9WH\nz7i+RoFZKjW1Do3jtnymlksoeTdqM5n0frmPt6UCgYBjILhOa7V0IzAoc1V0D2hl\neRNUILqk56/b2g/jpgzn5XLYqI7izVj/j0tpmKdtoq8X8LrPybE9WgqcbRD1fYzs\nXIg33UvUGYmO3qujXbxXPTDx14ZBiThMmUyDIMyi+fQiZl2fDB1Sz061vobxViOl\noF3KEYc/Fac2zJq70+zelQ==\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-fbsvc@federation-16c7a.iam.gserviceaccount.com",
    "client_id": "110350408404502535551",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40federation-16c7a.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# Configuration des notifications FCM
FCM_NOTIFICATION_SETTINGS = {
    'DEFAULT_SOUND': 'default',
    'DEFAULT_CHANNEL_ID': 'federation_channel',
    'DEFAULT_PRIORITY': 'high',
    'DEFAULT_BADGE': 1,
    'CLEANUP_INACTIVE_DAYS': 30,  # Jours avant de marquer un token comme inactif
}

# ============================================================================
# CONFIGURATION EMAIL SMTP GMAIL
# ============================================================================

# Configuration SMTP Gmail pour l'envoi d'emails
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False


# Configuration des emails (à remplacer par vos vraies valeurs)
EMAIL_HOST_USER = 'ayoubramezkhoja2003@gmail.com'  # Votre adresse Gmail
EMAIL_HOST_PASSWORD = 'ewcc dfah pbhq cigi'  # Mot de passe d'application Gmail (16 caractères)
DEFAULT_FROM_EMAIL = 'ayoubramezkhoja2003@gmail.com'  # Email expéditeur par défaut

# Configuration pour les emails de réinitialisation de mot de passe
# Configuration dynamique selon l'environnement
import os

# Déterminer l'URL du frontend selon l'environnement
if os.environ.get('DJANGO_ENV') == 'production' or not DEBUG:
    # Production (Vercel)
    FRONTEND_RESET_URL = 'https://federation-mobile.vercel.app/reset-password/'
else:
    # Développement local
    FRONTEND_RESET_URL = 'http://localhost:3000/reset-password/'

PASSWORD_RESET_SETTINGS = {
    'TOKEN_EXPIRY_MINUTES': 5,  # Durée de validité du token en minutes (sécurité optimale)
    'EMAIL_SUBJECT_PREFIX': '[Fédération Tunisienne de Football] ',
    'FRONTEND_RESET_URL': FRONTEND_RESET_URL,  # URL dynamique selon l'environnement
    'EMAIL_TEMPLATE_NAME': 'password_reset_email.html',
    'MAX_ATTEMPTS_PER_HOUR': 20,  # Maximum 20 tentatives par email par heure
    'AUTO_CLEANUP_HOURS': 1,  # Nettoyer les anciens tokens après 1 heure
}
