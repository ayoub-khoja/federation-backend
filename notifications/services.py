#!/usr/bin/env python3
"""
Service de notifications push Web pour les arbitres
"""

import json
import requests
from typing import List, Dict, Any
from django.conf import settings
from django.utils import timezone
from pywebpush import webpush, WebPushException
from accounts.models import Arbitre, PushSubscription

class PushNotificationService:
    """Service pour envoyer des notifications push aux arbitres"""
    
    def __init__(self):
        # Essayer d'abord les variables d'environnement
        self.vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', None)
        self.vapid_public_key = getattr(settings, 'VAPID_PUBLIC_KEY', None)
        self.vapid_email = getattr(settings, 'VAPID_EMAIL', 'admin@arbitrage.tn')
        
        # Si pas de clés dans settings, utiliser la configuration par défaut
        if not self.vapid_private_key:
            try:
                from backend.vapid_config import VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_EMAIL
                self.vapid_private_key = VAPID_PRIVATE_KEY
                self.vapid_public_key = VAPID_PUBLIC_KEY
                self.vapid_email = VAPID_EMAIL
                print("🔑 Utilisation des clés VAPID configurées")
            except ImportError:
                try:
                    import sys
                    import os
                    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
                    from vapid_config import VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY, VAPID_EMAIL
                    self.vapid_private_key = VAPID_PRIVATE_KEY
                    self.vapid_public_key = VAPID_PUBLIC_KEY
                    self.vapid_email = VAPID_EMAIL
                    print("🔑 Utilisation des clés VAPID configurées")
                except ImportError:
                    print("⚠️ Aucune clé VAPID trouvée, notifications désactivées")
                    self.vapid_private_key = "test_key"
                    self.vapid_public_key = "test_key"
    
    def send_notification_to_arbitres(
        self, 
        arbitres: List[Arbitre], 
        title: str, 
        body: str, 
        data: Dict[str, Any] = None,
        icon: str = None,
        badge: str = None,
        tag: str = None
    ) -> Dict[str, Any]:
        """
        Envoyer une notification push à une liste d'arbitres
        
        Args:
            arbitres: Liste des arbitres à notifier
            title: Titre de la notification
            body: Corps de la notification
            data: Données supplémentaires à envoyer
            icon: URL de l'icône
            badge: URL du badge
            tag: Tag pour grouper les notifications
        
        Returns:
            Dict avec le statut des envois
        """
        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for arbitre in arbitres:
            try:
                # Récupérer tous les abonnements actifs de l'arbitre
                subscriptions = PushSubscription.objects.filter(
                    arbitre=arbitre,
                    is_active=True
                )
                
                for subscription in subscriptions:
                    success = self._send_single_notification(
                        subscription, title, body, data, icon, badge, tag
                    )
                    
                    if success:
                        results['success'] += 1
                        # Mettre à jour la date de dernière utilisation
                        subscription.last_used = timezone.now()
                        subscription.save()
                    else:
                        results['failed'] += 1
                        
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Erreur pour {arbitre.get_full_name()}: {str(e)}")
        
        return results
    
    def _send_single_notification(
        self, 
        subscription: PushSubscription, 
        title: str, 
        body: str, 
        data: Dict[str, Any] = None,
        icon: str = None,
        badge: str = None,
        tag: str = None
    ) -> bool:
        """Envoyer une notification à un abonnement spécifique"""
        
        try:
            # Préparer le payload de la notification
            payload = {
                'title': title,
                'body': body,
                'icon': icon or '/static/images/notification-icon.png',
                'badge': badge or '/static/images/badge-icon.png',
                'tag': tag,
                'data': data or {},
                'timestamp': timezone.now().isoformat()
            }
            
            # Détecter le type d'endpoint
            from urllib.parse import urlparse
            parsed_url = urlparse(subscription.endpoint)
            is_fcm = 'fcm.googleapis.com' in subscription.endpoint
            
            print(f"🔔 Tentative d'envoi de notification:")
            print(f"   Endpoint: {subscription.endpoint}")
            print(f"   Type: {'FCM (Firebase)' if is_fcm else 'VAPID Standard'}")
            
            if is_fcm:
                # Pour FCM, utiliser une approche différente
                return self._send_fcm_notification(subscription, payload)
            else:
                # Pour les endpoints VAPID standard
                return self._send_vapid_notification(subscription, payload)
                
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi de notification: {e}")
            print(f"   Type d'erreur: {type(e).__name__}")
            print(f"   Détails: {str(e)}")
            import traceback
            print(f"   Stack trace: {traceback.format_exc()}")
            return False
    
    def _send_fcm_notification(self, subscription: PushSubscription, payload: Dict[str, Any]) -> bool:
        """Envoyer une notification via FCM (Firebase)"""
        try:
            print(f"🔥 Envoi via FCM...")
            
            # Pour FCM, l'audience doit être le schéma + hôte + port
            # Pas l'endpoint complet
            from urllib.parse import urlparse
            parsed_url = urlparse(subscription.endpoint)
            
            # Audience correcte pour FCM : schéma + hôte + port
            audience = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            print(f"   Audience FCM: {audience}")
            print(f"   Clés VAPID: {self.vapid_private_key[:20]}... / {self.vapid_public_key[:20]}...")
            
            # Essayer avec VAPID pour FCM
            response = webpush(
                subscription_info=subscription.subscription_info,
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims={
                    'sub': f'mailto:{self.vapid_email}',
                    'aud': audience
                }
            )
            
            print(f"✅ Réponse FCM: {response.status_code}")
            # FCM retourne 201 (Created) pour succès, pas 200
            return response.status_code in [200, 201]
            
        except Exception as e:
            print(f"❌ Erreur FCM: {e}")
            return False
    
    def _send_vapid_notification(self, subscription: PushSubscription, payload: Dict[str, Any]) -> bool:
        """Envoyer une notification via VAPID standard"""
        try:
            print(f"🔑 Envoi via VAPID...")
            
            # Extraire le domaine de l'endpoint pour l'audience VAPID
            from urllib.parse import urlparse
            parsed_url = urlparse(subscription.endpoint)
            audience = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            print(f"   Audience: {audience}")
            print(f"   Clés VAPID: {self.vapid_private_key[:20]}... / {self.vapid_public_key[:20]}...")
            
            response = webpush(
                subscription_info=subscription.subscription_info,
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims={
                    'sub': f'mailto:{self.vapid_email}',
                    'aud': audience
                }
            )
            
            # Vérifier la réponse
            if response.status_code == 200:
                return True
            else:
                # Si l'abonnement n'est plus valide, le désactiver
                if response.status_code in [404, 410]:
                    subscription.is_active = False
                    subscription.save()
                return False
                
        except WebPushException as e:
            # Gérer les erreurs Web Push
            print(f"❌ Erreur WebPush: {e}")
            if '410' in str(e) or '404' in str(e):
                # Abonnement expiré ou invalide
                subscription.is_active = False
                subscription.save()
            return False
            
        except Exception as e:
            print(f"❌ Erreur VAPID: {e}")
            return False
    
    def send_designation_notification(
        self, 
        arbitres: List[Arbitre], 
        match_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Envoyer une notification de désignation aux arbitres sélectionnés
        
        Args:
            arbitres: Liste des arbitres désignés
            match_info: Informations sur le match
        
        Returns:
            Dict avec le statut des envois
        """
        title = "🏆 Nouvelle Désignation d'Arbitrage"
        body = f"Vous avez été désigné pour le match {match_info.get('home_team', '')} vs {match_info.get('away_team', '')}"
        
        data = {
            'type': 'designation',
            'match_id': match_info.get('id'),
            'date_match': match_info.get('date'),
            'stade': match_info.get('stade'),
            'action_url': f'/matches/{match_info.get("id")}/designation'
        }
        
        return self.send_notification_to_arbitres(
            arbitres=arbitres,
            title=title,
            body=body,
            data=data,
            tag='designation'
        )

# Instance globale du service
push_service = PushNotificationService()
