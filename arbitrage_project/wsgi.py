"""
WSGI config for arbitrage_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Utiliser les settings de production si l'environnement est configuré
if os.environ.get('DJANGO_ENV') == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings_production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arbitrage_project.settings')

application = get_wsgi_application()














