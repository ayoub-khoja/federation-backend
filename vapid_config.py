#!/usr/bin/env python3
"""
Configuration VAPID pour les notifications push - FORMAT CORRIGÉ
"""

# Clés VAPID au bon format (DER brut, pas PEM)
VAPID_PRIVATE_KEY = "MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgsW95fAUD770Y-zt7ZxavOrgp9v3UTa5LR2__fhrHHj2hRANCAAQ6YIojXwMzLUarExcUSPyrxrWBo28BZ20ZJWypOPwIJmg4lyUIry98j9hy7TpcwTiqpF07WKQPYh7h0ihFZUXR"
VAPID_PUBLIC_KEY = "BDpgiiNfAzMtRqsTFxRI_KvGtYGjbwFnbRklbKk4_AgmaDiXJQivL3yP2HLtOlzBOKqkXTtYpA9iHuHSKEVlRdE"
VAPID_EMAIL = "admin@arbitrage.tn"

# Configuration des notifications
NOTIFICATION_CONFIG = {
    'default_icon': '/static/images/notification-icon.png',
    'default_badge': '/static/images/badge-icon.png',
    'default_tag': 'arbitrage',
    'require_interaction': True,
    'silent': False,
    'vibrate': [200, 100, 200],
    'actions': [
        {
            'action': 'view',
            'title': 'Voir',
            'icon': '/static/images/view-icon.png'
        },
        {
            'action': 'dismiss',
            'title': 'Fermer'
        }
    ]
}

# Types de notifications supportés
NOTIFICATION_TYPES = {
    'designation_created': {
        'title': '🏆 Nouvelle Désignation d\'Arbitrage',
        'icon': '/static/images/designation-icon.png',
        'tag': 'designation',
        'priority': 'high'
    },
    'designation_updated': {
        'title': '🔄 Désignation Mise à Jour',
        'icon': '/static/images/update-icon.png',
        'tag': 'designation_update',
        'priority': 'normal'
    },
    'designation_cancelled': {
        'title': '❌ Désignation Annulée',
        'icon': '/static/images/cancel-icon.png',
        'tag': 'designation_cancel',
        'priority': 'high'
    },
    'match_reminder': {
        'title': '⏰ Rappel de Match',
        'icon': '/static/images/reminder-icon.png',
        'tag': 'reminder',
        'priority': 'normal'
    }
}
