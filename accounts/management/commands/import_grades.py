"""
Commande Django pour importer les grades d'arbitrage depuis le fichier YAML
"""
import yaml
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from accounts.models import GradeArbitrage


class Command(BaseCommand):
    help = 'Importe les grades d\'arbitrage depuis le fichier YAML'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data/grades.yaml',
            help='Chemin vers le fichier YAML (relatif au dossier backend)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force la mise à jour des grades existants',
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
            
            if 'grades' not in data:
                raise CommandError('Le fichier YAML doit contenir une clé "grades"')
            
            grades_data = data['grades']
            self.stdout.write(f'Trouvé {len(grades_data)} grades dans le fichier YAML')
            
            created_count = 0
            updated_count = 0
            
            for grade_info in grades_data:
                # Vérifier les champs requis
                required_fields = ['nom', 'code']
                for field in required_fields:
                    if field not in grade_info:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Grade ignoré - champ "{field}" manquant: {grade_info}'
                            )
                        )
                        continue
                
                # Créer ou mettre à jour le grade
                grade, created = GradeArbitrage.objects.get_or_create(
                    code=grade_info['code'],
                    defaults={
                        'nom': grade_info['nom'],
                        'description': grade_info.get('description', ''),
                        'niveau': grade_info.get('niveau', 1),
                        'ordre': grade_info.get('ordre', 0),
                        'is_active': grade_info.get('is_active', True),
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Grade créé: {grade.nom} (Code: {grade.code})')
                    )
                elif options['force']:
                    # Mettre à jour le grade existant
                    grade.nom = grade_info['nom']
                    grade.description = grade_info.get('description', grade.description)
                    grade.niveau = grade_info.get('niveau', grade.niveau)
                    grade.ordre = grade_info.get('ordre', grade.ordre)
                    grade.is_active = grade_info.get('is_active', grade.is_active)
                    grade.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'↻ Grade mis à jour: {grade.nom} (Code: {grade.code})')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠ Grade existant ignoré: {grade.nom} '
                            f'(utilisez --force pour mettre à jour)'
                        )
                    )
            
            # Résumé
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('=== RÉSUMÉ ==='))
            self.stdout.write(f'Grades créés: {created_count}')
            self.stdout.write(f'Grades mis à jour: {updated_count}')
            self.stdout.write(f'Total en base: {GradeArbitrage.objects.count()}')
            
            # Afficher tous les grades actifs
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('=== GRADES ACTIFS ==='))
            for grade in GradeArbitrage.objects.filter(is_active=True).order_by('ordre', 'niveau', 'nom'):
                self.stdout.write(f'• {grade.nom} - Niveau {grade.niveau} (Code: {grade.code})')
                
        except yaml.YAMLError as e:
            raise CommandError(f'Erreur lors de la lecture du fichier YAML: {e}')
        except Exception as e:
            raise CommandError(f'Erreur inattendue: {e}')
