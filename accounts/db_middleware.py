"""
Middleware pour gérer les connexions à la base de données
"""
from django.db import connection

class DatabaseConnectionMiddleware:
    """
    Middleware pour fermer les connexions à la base de données après chaque requête
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Fermer la connexion à la base de données après chaque requête
        connection.close()
        
        return response
