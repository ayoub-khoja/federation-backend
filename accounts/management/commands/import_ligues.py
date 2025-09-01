"""
Commande Django pour importer les ligues d'arbitrage depuis le fichier YAML
"""
import yaml
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from accounts.models import LigueArbitrage


class Command(BaseCommand):
    help = 'Importe les ligues d\'arbitrage depuis le fichier YAML'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data/ligues.yaml',
            help='Chemin vers le fichier YAML (relatif au dossier backend)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force la mise à jour des ligues existantes',
        )

    def handle(self, *args, **options):
        # Construire le chemin complet vers le fichier YAML
        yaml_file = os.path.join(settings.BASE_DIR, options['file'])
        
        if not os.path.exists(yaml_file):
            raise CommandError(f'Le fichier {yaml_file} n\'existe pas')

        try:
            # Lire le fichier YAML
            with open(yaml_file, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
            
            if 'ligues_tunisiennes' not in data:
                raise CommandError('Le fichier YAML doit contenir une clé "ligues_tunisiennes"')
            
            ligues_data = data['ligues_tunisiennes']
            self.stdout.write(f'Trouvé {len(ligues_data)} ligues dans le fichier YAML')
            
            created_count = 0
            updated_count = 0
            
            for ligue_info in ligues_data:
                # Vérifier les champs requis
                required_fields = ['code', 'nom', 'region']
                for field in required_fields:
                    if field not in ligue_info:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Ligue ignorée - champ "{field}" manquant: {ligue_info}'
                            )
                        )
                        continue
                
                # Créer ou mettre à jour la ligue
                ligue, created = LigueArbitrage.objects.get_or_create(
                    code=ligue_info['code'],
                    defaults={
                        'nom': ligue_info['nom'],
                        'region': ligue_info['region'],
                        'active': ligue_info.get('active', True),
                        'ordre': ligue_info.get('ordre', 0),
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Ligue créée: {ligue.nom}')
                    )
                elif options['force']:
                    # Mettre à jour la ligue existante
                    ligue.nom = ligue_info['nom']
                    ligue.region = ligue_info['region']
                    ligue.active = ligue_info.get('active', True)
                    ligue.ordre = ligue_info.get('ordre', 0)
                    ligue.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'↻ Ligue mise à jour: {ligue.nom}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Ligue existante ignorée: {ligue.nom} '
                            f'(utilisez --force pour mettre à jour)'
                        )
                    )
            
            # Résumé
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('=== RÉSUMÉ ==='))
            self.stdout.write(f'Ligues créées: {created_count}')
            self.stdout.write(f'Ligues mises à jour: {updated_count}')
            self.stdout.write(f'Total en base: {LigueArbitrage.objects.count()}')
            
            # Afficher toutes les ligues actives
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('=== LIGUES ACTIVES ==='))
            for ligue in LigueArbitrage.objects.filter(active=True).order_by('ordre', 'nom'):
                self.stdout.write(f'• {ligue.nom} ({ligue.region}) - Code: {ligue.code}')
                
        except yaml.YAMLError as e:
            raise CommandError(f'Erreur lors de la lecture du fichier YAML: {e}')
        except Exception as e:
            raise CommandError(f'Erreur inattendue: {e}')


