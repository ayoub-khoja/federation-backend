"""
Commande Django pour mettre à jour automatiquement les statuts des matchs
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from matches.models import Match

class Command(BaseCommand):
    help = 'Met à jour automatiquement les statuts des matchs selon leur date'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche les changements sans les appliquer',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        today = date.today()
        
        self.stdout.write(
            self.style.SUCCESS(f'🔄 Mise à jour des statuts des matchs (Date: {today})')
        )
        
        # Récupérer tous les matchs
        all_matches = Match.objects.all()
        total_matches = all_matches.count()
        
        if total_matches == 0:
            self.stdout.write(
                self.style.WARNING('❌ Aucun match trouvé')
            )
            return
        
        self.stdout.write(f'📊 Total des matchs: {total_matches}')
        
        # Statistiques avant
        status_before = {}
        for match in all_matches:
            status = match.status
            status_before[status] = status_before.get(status, 0) + 1
        
        self.stdout.write('\n📋 Statuts actuels:')
        for status, count in status_before.items():
            self.stdout.write(f'   {status}: {count} match(s)')
        
        # Mettre à jour les statuts
        updated_count = 0
        for match in all_matches:
            old_status = match.status
            new_status = None
            
            if match.match_date < today:
                new_status = 'completed'
            elif match.match_date == today:
                new_status = 'in_progress'
            else:
                new_status = 'scheduled'
            
            if old_status != new_status:
                if not dry_run:
                    match.status = new_status
                    match.save()
                
                updated_count += 1
                self.stdout.write(
                    f'   {"✅" if not dry_run else "🔍"} {match.home_team} vs {match.away_team} '
                    f'({match.match_date}): {old_status} → {new_status}'
                )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'\n🔍 Mode test: {updated_count} match(s) seraient mis à jour')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ {updated_count} match(s) mis à jour')
            )
        
        # Statistiques après (si pas en mode test)
        if not dry_run and updated_count > 0:
            self.stdout.write('\n📋 Nouveaux statuts:')
            status_after = {}
            for match in Match.objects.all():
                status = match.status
                status_after[status] = status_after.get(status, 0) + 1
            
            for status, count in status_after.items():
                self.stdout.write(f'   {status}: {count} match(s)')





