"""
Commande Django pour nettoyer automatiquement les anciens tokens de réinitialisation de mot de passe
"""
from django.core.management.base import BaseCommand
from accounts.models import PasswordResetToken


class Command(BaseCommand):
    help = 'Nettoie automatiquement les anciens tokens de réinitialisation de mot de passe'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Affiche ce qui serait supprimé sans effectuer la suppression',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('Mode simulation - aucune suppression ne sera effectuée')
            )
        
        # Nettoyer les anciens tokens
        deleted_count = PasswordResetToken.cleanup_old_tokens()
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'Simulation : {deleted_count} tokens seraient supprimés')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'✅ {deleted_count} anciens tokens supprimés avec succès')
            )
            
            if deleted_count > 0:
                self.stdout.write(
                    self.style.SUCCESS('🧹 Nettoyage automatique terminé')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✨ Aucun token à nettoyer')
                )
















