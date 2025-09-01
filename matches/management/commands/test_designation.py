"""
Commande Django pour tester la création de désignations et les notifications
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import Arbitre
from matches.models import Match, Designation
from datetime import date, time

class Command(BaseCommand):
    help = 'Créer une désignation de test pour déclencher les notifications push'

    def add_arguments(self, parser):
        parser.add_argument(
            '--arbitre-id',
            type=int,
            help='ID de l\'arbitre à désigner'
        )
        parser.add_argument(
            '--match-id',
            type=int,
            help='ID du match pour la désignation'
        )

    def handle(self, *args, **options):
        try:
            # Récupérer l'arbitre
            arbitre_id = options.get('arbitre_id')
            if arbitre_id:
                arbitre = Arbitre.objects.get(id=arbitre_id)
            else:
                # Prendre le premier arbitre disponible
                arbitre = Arbitre.objects.first()
                if not arbitre:
                    self.stdout.write(
                        self.style.ERROR('❌ Aucun arbitre trouvé dans la base de données')
                    )
                    return

            # Récupérer ou créer un match
            match_id = options.get('match_id')
            if match_id:
                match = Match.objects.get(id=match_id)
            else:
                # Créer un match de test
                match = Match.objects.create(
                    match_type='ligue1',
                    category='senior',
                    stadium='Stade Olympique de Radès',
                    match_date=date.today() + timezone.timedelta(days=7),
                    match_time=time(20, 0),
                    home_team='Club Africain',
                    away_team='Étoile du Sahel',
                    description='Match de test pour les notifications',
                    referee=arbitre,
                    status='scheduled'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Match créé: {match}')
                )

            # Créer une désignation
            designation = Designation.objects.create(
                match=match,
                arbitre=arbitre,
                type_designation='arbitre_principal',
                status='proposed',
                commentaires='Désignation de test pour les notifications push'
            )

            self.stdout.write(
                self.style.SUCCESS(f'✅ Désignation créée: {designation}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'🔔 Notification push envoyée à {arbitre.get_full_name()}')
            )
            self.stdout.write(
                self.style.SUCCESS(f'📱 Vérifiez votre navigateur pour la notification')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur: {e}')
            )
