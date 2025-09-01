from django.apps import AppConfig


class MatchesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'matches'
    verbose_name = 'Gestion des Matchs'
    
    def ready(self):
        """Importer les signaux quand l'app est prête"""
        import matches.signals






