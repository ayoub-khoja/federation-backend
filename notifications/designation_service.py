#!/usr/bin/env python3
"""
Service de notifications automatiques pour les désignations d'arbitrage
"""

from typing import List, Dict, Any
from django.utils import timezone
from accounts.models import Arbitre, PushSubscription
from .services import push_service

class DesignationNotificationService:
    """Service pour envoyer des notifications automatiques lors de la création de désignations"""
    
    @staticmethod
    def notify_designation_created(arbitres: List[Arbitre], match_info: Dict[str, Any]):
        """
        Envoyer une notification automatique aux arbitres désignés
        
        Args:
            arbitres: Liste des arbitres désignés
            match_info: Informations sur le match
        """
        try:
            # Envoyer la notification via le service push
            result = push_service.send_designation_notification(
                arbitres=arbitres,
                match_info=match_info
            )
            
            print(f"🔔 Notifications de désignation envoyées: {result}")
            return result
            
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi des notifications de désignation: {e}")
            return {
                'success': 0,
                'failed': len(arbitres),
                'errors': [str(e)]
            }
    
    @staticmethod
    def notify_designation_updated(arbitres: List[Arbitre], match_info: Dict[str, Any]):
        """
        Envoyer une notification de mise à jour de désignation
        
        Args:
            arbitres: Liste des arbitres concernés
            match_info: Informations mises à jour sur le match
        """
        try:
            title = "🔄 Désignation Mise à Jour"
            body = f"Mise à jour de votre désignation pour le match {match_info.get('home_team', '')} vs {match_info.get('away_team', '')}"
            
            data = {
                'type': 'designation_updated',
                'match_id': match_info.get('id'),
                'date_match': match_info.get('date'),
                'stade': match_info.get('stade'),
                'action_url': f'/matches/{match_info.get("id")}/designation'
            }
            
            result = push_service.send_notification_to_arbitres(
                arbitres=arbitres,
                title=title,
                body=body,
                data=data,
                tag='designation_updated'
            )
            
            print(f"🔄 Notifications de mise à jour envoyées: {result}")
            return result
            
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi des notifications de mise à jour: {e}")
            return {
                'success': 0,
                'failed': len(arbitres),
                'errors': [str(e)]
            }
    
    @staticmethod
    def notify_designation_cancelled(arbitres: List[Arbitre], match_info: Dict[str, Any]):
        """
        Envoyer une notification d'annulation de désignation
        
        Args:
            arbitres: Liste des arbitres concernés
            match_info: Informations sur le match annulé
        """
        try:
            title = "❌ Désignation Annulée"
            body = f"Votre désignation pour le match {match_info.get('home_team', '')} vs {match_info.get('away_team', '')} a été annulée"
            
            data = {
                'type': 'designation_cancelled',
                'match_id': match_info.get('id'),
                'date_match': match_info.get('date'),
                'stade': match_info.get('stade'),
                'action_url': '/designations'
            }
            
            result = push_service.send_notification_to_arbitres(
                arbitres=arbitres,
                title=title,
                body=body,
                data=data,
                tag='designation_cancelled'
            )
            
            print(f"❌ Notifications d'annulation envoyées: {result}")
            return result
            
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi des notifications d'annulation: {e}")
            return {
                'success': 0,
                'failed': len(arbitres),
                'errors': [str(e)]
            }

# Instance globale du service
designation_notification_service = DesignationNotificationService()
