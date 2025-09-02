"""
Configuration Firebase Cloud Messaging (FCM) pour les notifications push
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.contrib.auth import get_user_model

# Configuration du logging
logger = logging.getLogger(__name__)

# Import conditionnel de Firebase (sera installé plus tard)
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("Firebase Admin SDK non installé. Les notifications FCM ne fonctionneront pas.")

def initialize_firebase():
    """Initialiser Firebase Admin SDK"""
    if not FIREBASE_AVAILABLE:
        logger.error("Firebase Admin SDK non disponible")
        return False
    
    if not firebase_admin._apps:
        try:
            # Chemin vers le fichier de clé de service Firebase
            service_account_path = getattr(settings, 'FIREBASE_SERVICE_ACCOUNT_PATH', None)
            
            if service_account_path and os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialisé avec succès")
                return True
            else:
                # Essayer avec les variables d'environnement
                firebase_config = getattr(settings, 'FIREBASE_CONFIG', None)
                if firebase_config:
                    if isinstance(firebase_config, str):
                        firebase_config = json.loads(firebase_config)
                    
                    cred = credentials.Certificate(firebase_config)
                    firebase_admin.initialize_app(cred)
                    logger.info("Firebase Admin SDK initialisé avec les variables d'environnement")
                    return True
                else:
                    logger.error("Configuration Firebase non trouvée")
                    return False
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de Firebase: {e}")
            return False
    
    return True

def send_notification_to_platform(
    fcm_token: str, 
    title: str, 
    body: str, 
    data: Optional[Dict[str, str]] = None, 
    platform: str = 'web'
) -> bool:
    """
    Envoyer une notification à une plateforme spécifique
    
    Args:
        fcm_token: Token FCM de l'appareil
        title: Titre de la notification
        body: Corps de la notification
        data: Données supplémentaires (optionnel)
        platform: Type de plateforme ('ios', 'android', 'web')
    
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    if not FIREBASE_AVAILABLE:
        logger.error("Firebase Admin SDK non disponible")
        return False
    
    if not initialize_firebase():
        return False
    
    try:
        # Configuration de base du message
        # Convertir toutes les données en chaînes de caractères pour FCM
        fcm_data = {}
        if data:
            for key, value in data.items():
                fcm_data[str(key)] = str(value)
        
        message_data = {
            'notification': messaging.Notification(
                title=title,
                body=body,
            ),
            'data': fcm_data,
            'token': fcm_token,
        }
        
        # Configuration spécifique selon la plateforme
        if platform == 'ios':
            message_data['apns'] = messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default',
                        badge=1,
                        alert=messaging.ApsAlert(
                            title=title,
                            body=body
                        )
                    )
                )
            )
        elif platform == 'android':
            message_data['android'] = messaging.AndroidConfig(
                notification=messaging.AndroidNotification(
                    sound='default',
                    channel_id='federation_channel',
                    priority='high',
                    click_action='FLUTTER_NOTIFICATION_CLICK'
                )
            )
        
        # Créer et envoyer le message
        message = messaging.Message(**message_data)
        response = messaging.send(message)
        
        logger.info(f'Notification {platform} envoyée avec succès: {response}')
        return True
        
    except Exception as e:
        logger.error(f'Erreur lors de l\'envoi de la notification {platform}: {e}')
        return False

def send_notification_to_user(
    user, 
    title: str, 
    body: str, 
    data: Optional[Dict[str, str]] = None
) -> Dict[str, int]:
    """
    Envoyer une notification à un utilisateur sur toutes ses plateformes
    
    Args:
        user: Utilisateur (Arbitre, Commissaire ou Admin)
        title: Titre de la notification
        body: Corps de la notification
        data: Données supplémentaires (optionnel)
    
    Returns:
        Dict avec le nombre de notifications envoyées par plateforme
    """
    from accounts.models import FCMToken
    
    results = {'ios': 0, 'android': 0, 'web': 0, 'errors': 0}
    
    try:
        # Récupérer tous les tokens actifs de l'utilisateur
        fcm_tokens = FCMToken.objects.filter(
            is_active=True,
            **{
                f'{user.__class__.__name__.lower()}': user
            }
        )
        
        for fcm_token in fcm_tokens:
            success = send_notification_to_platform(
                fcm_token.token, 
                title, 
                body, 
                data, 
                fcm_token.device_type
            )
            
            if success:
                results[fcm_token.device_type] += 1
                # Mettre à jour la dernière utilisation
                fcm_token.save()
            else:
                results['errors'] += 1
                
    except Exception as e:
        logger.error(f'Erreur lors de l\'envoi de notification à l\'utilisateur: {e}')
        results['errors'] += 1
    
    return results

def send_notification_to_all_platforms(
    title: str, 
    body: str, 
    data: Optional[Dict[str, str]] = None,
    device_types: Optional[List[str]] = None
) -> Dict[str, int]:
    """
    Envoyer une notification à tous les utilisateurs sur toutes les plateformes
    
    Args:
        title: Titre de la notification
        body: Corps de la notification
        data: Données supplémentaires (optionnel)
        device_types: Types d'appareils ciblés (optionnel)
    
    Returns:
        Dict avec le nombre de notifications envoyées par plateforme
    """
    from accounts.models import FCMToken
    
    results = {'ios': 0, 'android': 0, 'web': 0, 'errors': 0}
    
    try:
        # Récupérer tous les tokens actifs
        fcm_tokens = FCMToken.objects.filter(is_active=True)
        
        if device_types:
            fcm_tokens = fcm_tokens.filter(device_type__in=device_types)
        
        for fcm_token in fcm_tokens:
            success = send_notification_to_platform(
                fcm_token.token, 
                title, 
                body, 
                data, 
                fcm_token.device_type
            )
            
            if success:
                results[fcm_token.device_type] += 1
                # Mettre à jour la dernière utilisation
                fcm_token.save()
            else:
                results['errors'] += 1
                
    except Exception as e:
        logger.error(f'Erreur lors de l\'envoi de notification globale: {e}')
        results['errors'] += 1
    
    return results

def send_notification_to_ligue(
    ligue_id: int,
    title: str, 
    body: str, 
    data: Optional[Dict[str, str]] = None
) -> Dict[str, int]:
    """
    Envoyer une notification à tous les utilisateurs d'une ligue spécifique
    
    Args:
        ligue_id: ID de la ligue
        title: Titre de la notification
        body: Corps de la notification
        data: Données supplémentaires (optionnel)
    
    Returns:
        Dict avec le nombre de notifications envoyées par plateforme
    """
    from accounts.models import FCMToken, Arbitre, Commissaire
    
    results = {'ios': 0, 'android': 0, 'web': 0, 'errors': 0}
    
    try:
        # Récupérer tous les tokens des utilisateurs de la ligue
        fcm_tokens = FCMToken.objects.filter(
            is_active=True
        ).filter(
            models.Q(arbitre__ligue_id=ligue_id) | 
            models.Q(commissaire__ligue_id=ligue_id)
        )
        
        for fcm_token in fcm_tokens:
            success = send_notification_to_platform(
                fcm_token.token, 
                title, 
                body, 
                data, 
                fcm_token.device_type
            )
            
            if success:
                results[fcm_token.device_type] += 1
                # Mettre à jour la dernière utilisation
                fcm_token.save()
            else:
                results['errors'] += 1
                
    except Exception as e:
        logger.error(f'Erreur lors de l\'envoi de notification à la ligue {ligue_id}: {e}')
        results['errors'] += 1
    
    return results

def cleanup_inactive_tokens():
    """
    Nettoyer les tokens FCM inactifs ou invalides
    """
    from accounts.models import FCMToken
    from django.utils import timezone
    from datetime import timedelta
    
    try:
        # Marquer comme inactifs les tokens non utilisés depuis plus de 30 jours
        cutoff_date = timezone.now() - timedelta(days=30)
        inactive_tokens = FCMToken.objects.filter(
            last_used__lt=cutoff_date,
            is_active=True
        )
        
        count = inactive_tokens.update(is_active=False)
        logger.info(f'{count} tokens FCM marqués comme inactifs')
        
        return count
        
    except Exception as e:
        logger.error(f'Erreur lors du nettoyage des tokens: {e}')
        return 0

def get_notification_stats() -> Dict[str, Any]:
    """
    Obtenir les statistiques des notifications FCM
    
    Returns:
        Dict avec les statistiques
    """
    from accounts.models import FCMToken
    
    try:
        stats = {
            'total_tokens': FCMToken.objects.count(),
            'active_tokens': FCMToken.objects.filter(is_active=True).count(),
            'by_platform': {},
            'by_user_type': {
                'arbitres': FCMToken.objects.filter(arbitre__isnull=False).count(),
                'commissaires': FCMToken.objects.filter(commissaire__isnull=False).count(),
                'admins': FCMToken.objects.filter(admin__isnull=False).count(),
            }
        }
        
        # Statistiques par plateforme
        for device_type, _ in FCMToken.DEVICE_TYPE_CHOICES:
            stats['by_platform'][device_type] = FCMToken.objects.filter(
                device_type=device_type,
                is_active=True
            ).count()
        
        return stats
        
    except Exception as e:
        logger.error(f'Erreur lors de la récupération des statistiques: {e}')
        return {}
