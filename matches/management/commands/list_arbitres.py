"""
Commande Django pour lister tous les arbitres disponibles
"""
from django.core.management.base import BaseCommand
from accounts.models import Arbitre

class Command(BaseCommand):
    help = 'Lister tous les arbitres disponibles dans la base de données'

    def handle(self, *args, **options):
        try:
            # Récupérer tous les arbitres
            arbitres = Arbitre.objects.all()
            
            if not arbitres.exists():
                self.stdout.write(
                    self.style.WARNING('⚠️ Aucun arbitre trouvé dans la base de données')
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS(f'📋 {arbitres.count()} arbitre(s) trouvé(s):\n')
            )
            
            for arbitre in arbitres:
                self.stdout.write(
                    f"  ID: {arbitre.id} | Nom: {arbitre.get_full_name()} | "
                    f"Grade: {getattr(arbitre, 'grade', 'N/A')} | "
                    f"Téléphone: {arbitre.phone_number}"
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'\n💡 Utilisez l\'ID d\'un arbitre pour tester:')
            )
            self.stdout.write(
                f'  python manage.py test_designation --arbitre-id {arbitres.first().id}'
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur: {e}')
            )
