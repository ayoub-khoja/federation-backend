"""
Vues API pour la gestion des matchs
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Match, MatchEvent, Designation, TypeMatch, Categorie
from .serializers import (
    MatchSerializer,
    MatchCreateSerializer,
    MatchUpdateSerializer,
    MatchListSerializer,
    MatchEventSerializer,
    DesignationSerializer,
    DesignationCreateSerializer,
    DesignationUpdateSerializer,
    DesignationListSerializer,
    TypeMatchSerializer,
    CategorieSerializer
)

class MatchListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des matchs"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MatchCreateSerializer
        return MatchSerializer
    
    def get_queryset(self):
        """Retourne les matchs de l'arbitre connecté"""
        return Match.objects.filter(referee=self.request.user).select_related('type_match', 'categorie', 'referee')
    
    def list(self, request, *args, **kwargs):
        """Lister les matchs de l'arbitre connecté avec toutes les données"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'message': f'{queryset.count()} match(s) trouvé(s)',
            'matches': serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            match = serializer.save()
            return Response({
                'success': True,
                'message': 'Match créé avec succès',
                'match': MatchSerializer(match).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Erreur lors de la création du match',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class MatchDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour consulter, modifier et supprimer un match"""
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Seuls les matchs de l'arbitre connecté"""
        return Match.objects.filter(referee=self.request.user).select_related('type_match', 'categorie', 'referee')
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return MatchUpdateSerializer
        return MatchSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Récupérer un match spécifique avec toutes les données"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'success': True,
            'message': 'Match récupéré avec succès',
            'match': serializer.data
        })

@api_view(['GET'])
def match_statistics(request):
    """Statistiques des matchs de l'arbitre"""
    user_matches = Match.objects.filter(referee=request.user)
    
    # Calculs des statistiques
    total_matches = user_matches.count()
    completed_matches = user_matches.filter(status='completed').count()
    upcoming_matches = user_matches.filter(
        match_date__gte=timezone.now().date(),
        status='scheduled'
    ).count()
    
    # Matchs par type
    match_types = {}
    for choice in Match.MATCH_TYPE_CHOICES:
        count = user_matches.filter(match_type=choice[0]).count()
        if count > 0:
            match_types[choice[1]] = count
    
    # Prochains matchs (7 prochains jours)
    next_week = timezone.now().date() + timedelta(days=7)
    upcoming_week = user_matches.filter(
        match_date__range=[timezone.now().date(), next_week],
        status='scheduled'
    ).order_by('match_date', 'match_time')
    
    return Response({
        'success': True,
        'statistics': {
            'total_matches': total_matches,
            'completed_matches': completed_matches,
            'upcoming_matches': upcoming_matches,
            'match_types': match_types,
            'completion_rate': round((completed_matches / total_matches * 100) if total_matches > 0 else 0, 2)
        },
        'upcoming_matches': MatchListSerializer(upcoming_week, many=True).data
    })

@api_view(['POST'])
def complete_match(request, match_id):
    """Marquer un match comme terminé avec le score"""
    try:
        match = Match.objects.get(id=match_id, referee=request.user)
    except Match.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Match non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    home_score = request.data.get('home_score')
    away_score = request.data.get('away_score')
    match_report = request.data.get('match_report', '')
    incidents = request.data.get('incidents', '')
    
    if home_score is None or away_score is None:
        return Response({
            'success': False,
            'message': 'Le score des deux équipes est requis'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        match.home_score = int(home_score)
        match.away_score = int(away_score)
        match.status = 'completed'
        match.match_report = match_report
        match.incidents = incidents
        match.save()
        
        return Response({
            'success': True,
            'message': 'Match marqué comme terminé',
            'match': MatchSerializer(match).data
        })
    except ValueError:
        return Response({
            'success': False,
            'message': 'Score invalide'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def recent_matches(request):
    """Récupérer les matchs récents de l'arbitre"""
    limit = int(request.GET.get('limit', 10))
    matches = Match.objects.filter(
        referee=request.user
    ).order_by('-match_date', '-match_time')[:limit]
    
    return Response({
        'success': True,
        'matches': MatchListSerializer(matches, many=True).data
    })

@api_view(['GET'])
def upcoming_matches(request):
    """Récupérer les prochains matchs de l'arbitre"""
    matches = Match.objects.filter(
        referee=request.user,
        match_date__gte=timezone.now().date(),
        status__in=['scheduled', 'in_progress']
    ).order_by('match_date', 'match_time')
    
    return Response({
        'success': True,
        'matches': MatchListSerializer(matches, many=True).data
    })

# ===== VUES POUR LES DÉSIGNATIONS =====

class DesignationListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des désignations"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DesignationCreateSerializer
        return DesignationListSerializer
    
    def get_queryset(self):
        """Retourne toutes les désignations (pour les administrateurs)"""
        if self.request.user.is_staff:
            return Designation.objects.all()
        # Pour les arbitres, retourner leurs propres désignations
        return Designation.objects.filter(arbitre=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            designation = serializer.save()
            
            # Envoyer automatiquement la notification push
            try:
                from notifications.services import push_service
                
                match_info = {
                    'id': designation.match.id,
                    'home_team': designation.match.home_team,
                    'away_team': designation.match.away_team,
                    'date': designation.match.match_date.isoformat(),
                    'stade': designation.match.stadium,
                    'type_designation': designation.get_type_designation_display()
                }
                
                result = push_service.send_designation_notification(
                    [designation.arbitre], 
                    match_info
                )
                
                if result['success'] > 0:
                    designation.marquer_notification_envoyee()
                
            except Exception as e:
                print(f"Erreur notification push: {e}")
            
            return Response({
                'success': True,
                'message': 'Désignation créée avec succès',
                'designation': DesignationSerializer(designation).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Erreur lors de la création de la désignation',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class DesignationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour consulter, modifier et supprimer une désignation"""
    serializer_class = DesignationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Seuls les administrateurs peuvent voir toutes les désignations"""
        if self.request.user.is_staff:
            return Designation.objects.all()
        # Les arbitres voient leurs propres désignations
        return Designation.objects.filter(arbitre=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DesignationUpdateSerializer
        return DesignationSerializer

@api_view(['POST'])
def accept_designation(request, designation_id):
    """Accepter une désignation"""
    try:
        designation = Designation.objects.get(
            id=designation_id, 
            arbitre=request.user
        )
    except Designation.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Désignation non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if designation.status != 'proposed':
        return Response({
            'success': False,
            'message': 'Cette désignation ne peut plus être acceptée'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    designation.accepter()
    
    return Response({
        'success': True,
        'message': 'Désignation acceptée avec succès',
        'designation': DesignationSerializer(designation).data
    })

@api_view(['POST'])
def decline_designation(request, designation_id):
    """Refuser une désignation"""
    try:
        designation = Designation.objects.get(
            id=designation_id, 
            arbitre=request.user
        )
    except Designation.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Désignation non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if designation.status != 'proposed':
        return Response({
            'success': False,
            'message': 'Cette désignation ne peut plus être refusée'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    raison = request.data.get('raison', '')
    designation.refuser(raison)
    
    return Response({
        'success': True,
        'message': 'Désignation refusée',
        'designation': DesignationSerializer(designation).data
    })

@api_view(['GET'])
def designation_statistics(request):
    """Statistiques des désignations"""
    if request.user.is_staff:
        # Pour les administrateurs, toutes les désignations
        designations = Designation.objects.all()
    else:
        # Pour les arbitres, leurs propres désignations
        designations = Designation.objects.filter(arbitre=request.user)
    
    total = designations.count()
    accepted = designations.filter(status='accepted').count()
    declined = designations.filter(status='declined').count()
    pending = designations.filter(status='proposed').count()
    confirmed = designations.filter(status='confirmed').count()
    
    # Désignations par type
    types_stats = {}
    for choice in Designation.TYPE_CHOICES:
        count = designations.filter(type_designation=choice[0]).count()
        if count > 0:
            types_stats[choice[1]] = count
    
    return Response({
        'success': True,
        'statistics': {
            'total': total,
            'accepted': accepted,
            'declined': declined,
            'pending': pending,
            'confirmed': confirmed,
            'types': types_stats,
            'acceptance_rate': round((accepted / total * 100) if total > 0 else 0, 2)
        }
    })

@api_view(['GET'])
def my_designations(request):
    """Récupérer les désignations de l'arbitre connecté"""
    designations = Designation.objects.filter(
        arbitre=request.user
    ).order_by('-date_designation')
    
    return Response({
        'success': True,
        'designations': DesignationListSerializer(designations, many=True).data
    })

# ===== VUES POUR LES TYPES DE MATCH ET CATÉGORIES =====

@api_view(['GET'])
def match_types(request):
    """Récupérer tous les types de match actifs"""
    types = TypeMatch.objects.filter(is_active=True).order_by('ordre', 'nom')
    
    return Response({
        'success': True,
        'types': TypeMatchSerializer(types, many=True).data
    })

@api_view(['GET'])
def categories(request):
    """Récupérer toutes les catégories actives"""
    categories = Categorie.objects.filter(is_active=True).order_by('ordre', 'nom')
    
    return Response({
        'success': True,
        'categories': CategorieSerializer(categories, many=True).data
    })

@api_view(['GET'])
def match_roles(request):
    """Récupérer tous les rôles d'arbitrage disponibles"""
    from .models import Match
    
    roles = []
    for choice in Match.ROLE_CHOICES:
        roles.append({
            'value': choice[0],
            'label': choice[1]
        })
    
    return Response({
        'success': True,
        'roles': roles
    })





