"""
Signaux Django pour la gestion automatique des notifications
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Designation, Match
from notifications.services import push_service

@receiver(post_save, sender=Designation)
def send_designation_notification(sender, instance, created, **kwargs):
    """
    Envoyer une notification push automatiquement lors de la création d'une désignation
    """
    if created and instance.status in ['proposed', 'accepted', 'confirmed']:
        try:
            print(f"🔔 Désignation créée pour {instance.arbitre.get_full_name()}")
            
            # Préparer les informations du match
            match_info = {
                'id': instance.match.id,
                'home_team': instance.match.home_team,
                'away_team': instance.match.away_team,
                'date': instance.match.match_date.strftime('%d/%m/%Y'),
                'time': instance.match.match_time.strftime('%H:%M'),
                'stade': instance.match.stadium,
                'type_match': instance.match.type_match.nom if instance.match.type_match else "Non défini",
                'categorie': instance.match.categorie.nom if instance.match.categorie else "Non définie",
                'type_designation': instance.get_type_designation_display()
            }
            
            # Envoyer la notification via le nouveau système FCM
            from firebase_config import send_notification_to_user
            
            result = send_notification_to_user(
                user=instance.arbitre,
                title="🏆 Nouvelle Désignation d'Arbitrage",
                body=f"Vous avez été désigné pour le match {match_info['home_team']} vs {match_info['away_team']}",
                data={
                    'type': 'designation',
                    'match_id': str(match_info['id']),
                    'date_match': match_info['date'],
                    'stade': match_info['stade'],
                    'type_designation': match_info['type_designation']
                }
            )
            
            print(f"📤 Notification envoyée: {result}")
            
            # Marquer la notification comme envoyée
            if result.get('errors', 0) == 0:
                instance.notification_envoyee = True
                instance.date_notification = timezone.now()
                instance.save(update_fields=['notification_envoyee', 'date_notification'])
                print(f"✅ Notification marquée comme envoyée pour {instance.arbitre.get_full_name()}")
            else:
                print(f"❌ Échec de l'envoi de notification: {result}")
                
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi de notification: {e}")

@receiver(post_save, sender=Designation)
def send_designation_update_notification(sender, instance, created, **kwargs):
    """
    Envoyer une notification lors de la mise à jour du statut d'une désignation
    """
    if not created and instance.status in ['confirmed', 'cancelled']:
        try:
            print(f"🔄 Statut de désignation mis à jour: {instance.arbitre.get_full_name()} - {instance.get_status_display()}")
            
            # Préparer les informations
            match_info = {
                'id': instance.match.id,
                'home_team': instance.match.home_team,
                'away_team': instance.match.away_team,
                'date': instance.match.match_date.strftime('%d/%m/%Y'),
                'time': instance.match.match_time.strftime('%H:%M'),
                'stade': instance.match.stadium,
                'type_designation': instance.get_type_designation_display()
            }
            
            # Titre et message selon le statut
            if instance.status == 'confirmed':
                title = "✅ Désignation Confirmée"
                body = f"Votre désignation pour {match_info['home_team']} vs {match_info['away_team']} a été confirmée"
                tag = 'designation_confirmed'
            else:  # cancelled
                title = "❌ Désignation Annulée"
                body = f"Votre désignation pour {match_info['home_team']} vs {match_info['away_team']} a été annulée"
                tag = 'designation_cancelled'
            
            # Envoyer la notification
            result = push_service.send_notification_to_arbitres(
                arbitres=[instance.arbitre],
                title=title,
                body=body,
                data={
                    'type': 'designation_update',
                    'match_id': match_info['id'],
                    'status': instance.status,
                    'action_url': f'/matches/{match_info["id"]}/designation'
                },
                tag=tag
            )
            
            print(f"📤 Notification de mise à jour envoyée: {result}")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi de notification de mise à jour: {e}")

@receiver(post_delete, sender=Designation)
def send_designation_cancellation_notification(sender, instance, **kwargs):
    """
    Envoyer une notification lors de la suppression d'une désignation
    """
    try:
        print(f"🗑️ Désignation supprimée pour {instance.arbitre.get_full_name()}")
        
        # Préparer les informations
        match_info = {
            'id': instance.match.id,
            'home_team': instance.match.home_team,
            'away_team': instance.match.away_team,
            'date': instance.match.match_date.strftime('%d/%m/%Y'),
            'time': instance.match.match_time.strftime('%H:%M'),
            'stade': instance.match.stadium,
            'type_designation': instance.get_type_designation_display()
        }
        
        # Envoyer la notification
        result = push_service.send_notification_to_arbitres(
            arbitres=[instance.arbitre],
            title="🗑️ Désignation Supprimée",
            body=f"Votre désignation pour {match_info['home_team']} vs {match_info['away_team']} a été supprimée",
            data={
                'type': 'designation_deleted',
                'match_id': match_info['id'],
                'action_url': f'/matches/{match_info["id"]}/designation'
            },
            tag='designation_deleted'
        )
        
        print(f"📤 Notification de suppression envoyée: {result}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi de notification de suppression: {e}")
