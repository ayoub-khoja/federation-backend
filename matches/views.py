"""
Vues API pour la gestion des matchs
"""
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Match, MatchEvent, Designation, TypeMatch, Categorie, ExcuseArbitre, TarificationMatch
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
    CategorieSerializer,
    ExcuseArbitreSerializer,
    ExcuseArbitreCreateSerializer,
    ExcuseArbitreListSerializer,
    TarificationMatchSerializer,
    TarificationMatchListSerializer,
    TarificationMatchCreateSerializer,
    TarificationMatchUpdateSerializer
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

@api_view(['GET'])
def matches_by_type(request, type_code):
    """Récupérer les matchs sifflés par type de compétition"""
    # Cette vue est accessible sans authentification
    try:
        # Récupérer le type de match par code
        match_type = TypeMatch.objects.get(code=type_code, is_active=True)
    except TypeMatch.DoesNotExist:
        return Response({
            'success': False,
            'message': f'Type de match {type_code} non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Récupérer les matchs sifflés (terminés) de ce type
    matches = Match.objects.filter(
        type_match=match_type,
        status='completed'
    ).select_related('type_match', 'categorie', 'referee').order_by('-match_date', '-match_time')
    
    # Appliquer des filtres optionnels
    referee_id = request.GET.get('referee_id')
    if referee_id:
        matches = matches.filter(referee_id=referee_id)
    
    date_from = request.GET.get('date_from')
    if date_from:
        try:
            from datetime import datetime
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            matches = matches.filter(match_date__gte=date_from_obj)
        except ValueError:
            return Response({
                'success': False,
                'message': 'Format de date invalide. Utilisez YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    date_to = request.GET.get('date_to')
    if date_to:
        try:
            from datetime import datetime
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            matches = matches.filter(match_date__lte=date_to_obj)
        except ValueError:
            return Response({
                'success': False,
                'message': 'Format de date invalide. Utilisez YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Pagination
    page_size = int(request.GET.get('page_size', 20))
    page = int(request.GET.get('page', 1))
    
    start = (page - 1) * page_size
    end = start + page_size
    
    total_matches = matches.count()
    matches_page = matches[start:end]
    
    # Statistiques
    stats = {
        'total_matches': total_matches,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_matches + page_size - 1) // page_size,
        'has_next': end < total_matches,
        'has_previous': page > 1
    }
    
    return Response({
        'success': True,
        'message': f'{total_matches} match(s) de {match_type.nom} trouvé(s)',
        'type_info': {
            'id': match_type.id,
            'nom': match_type.nom,
            'code': match_type.code,
            'description': match_type.description
        },
        'statistics': stats,
        'matches': MatchListSerializer(matches_page, many=True).data
    })

# Vues spécifiques pour chaque type de compétition
class CompetitionMatchesView(generics.ListAPIView):
    """Vue générique pour les matchs de compétition"""
    permission_classes = [permissions.AllowAny]
    serializer_class = MatchListSerializer
    
    def get_queryset(self):
        type_code = self.kwargs['type_code']
        try:
            match_type = TypeMatch.objects.get(code=type_code, is_active=True)
            return Match.objects.filter(
                type_match=match_type,
                status='completed'
            ).select_related('type_match', 'categorie', 'referee').order_by('-match_date', '-match_time')
        except TypeMatch.DoesNotExist:
            return Match.objects.none()
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Si aucun match trouvé, vérifier si le type existe
        if not queryset.exists():
            # Récupérer le type de match pour vérifier s'il existe
            type_code = getattr(self, 'type_code', 'unknown')
            try:
                match_type = TypeMatch.objects.get(code=type_code, is_active=True)
                return Response({
                    'success': True,
                    'message': f'Aucun match trouvé pour {match_type.nom}',
                    'competition': {
                        'code': match_type.code,
                        'name': match_type.nom,
                        'description': match_type.description
                    },
                    'matches': []
                })
            except TypeMatch.DoesNotExist:
                return Response({
                    'success': False,
                    'message': f'Type de match {type_code} non trouvé'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Récupérer le type de match depuis le premier match
        match_type = queryset.first().type_match
        
        # Appliquer des filtres optionnels
        referee_id = request.GET.get('referee_id')
        if referee_id:
            queryset = queryset.filter(referee_id=referee_id)
        
        date_from = request.GET.get('date_from')
        if date_from:
            try:
                from datetime import datetime
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(match_date__gte=date_from_obj)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Format de date invalide (YYYY-MM-DD)'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        date_to = request.GET.get('date_to')
        if date_to:
            try:
                from datetime import datetime
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(match_date__lte=date_to_obj)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Format de date invalide (YYYY-MM-DD)'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'message': f'{queryset.count()} match(s) de {match_type.nom} trouvé(s)',
            'competition': {
                'code': match_type.code,
                'name': match_type.nom,
                'description': match_type.description
            },
            'matches': serializer.data
        })

# Vues spécifiques pour chaque type de compétition
class Ligue1MatchesView(CompetitionMatchesView):
    """Récupérer les matchs sifflés de Ligue 1"""
    type_code = 'L1'
    
    def get_queryset(self):
        try:
            match_type = TypeMatch.objects.get(code='L1', is_active=True)
            return Match.objects.filter(
                type_match=match_type,
                status='completed'
            ).select_related('type_match', 'categorie', 'referee').order_by('-match_date', '-match_time')
        except TypeMatch.DoesNotExist:
            return Match.objects.none()

class Ligue2MatchesView(CompetitionMatchesView):
    """Récupérer les matchs sifflés de Ligue 2"""
    type_code = 'L2'
    
    def get_queryset(self):
        try:
            match_type = TypeMatch.objects.get(code='L2', is_active=True)
            return Match.objects.filter(
                type_match=match_type,
                status='completed'
            ).select_related('type_match', 'categorie', 'referee').order_by('-match_date', '-match_time')
        except TypeMatch.DoesNotExist:
            return Match.objects.none()

class C1MatchesView(CompetitionMatchesView):
    """Récupérer les matchs sifflés de C1"""
    type_code = 'C1'
    
    def get_queryset(self):
        try:
            match_type = TypeMatch.objects.get(code='C1', is_active=True)
            return Match.objects.filter(
                type_match=match_type,
                status='completed'
            ).select_related('type_match', 'categorie', 'referee').order_by('-match_date', '-match_time')
        except TypeMatch.DoesNotExist:
            return Match.objects.none()

class C2MatchesView(CompetitionMatchesView):
    """Récupérer les matchs sifflés de C2"""
    type_code = 'C2'
    
    def get_queryset(self):
        try:
            match_type = TypeMatch.objects.get(code='C2', is_active=True)
            return Match.objects.filter(
                type_match=match_type,
                status='completed'
            ).select_related('type_match', 'categorie', 'referee').order_by('-match_date', '-match_time')
        except TypeMatch.DoesNotExist:
            return Match.objects.none()

class JeunesMatchesView(CompetitionMatchesView):
    """Récupérer les matchs sifflés de Jeunes"""
    type_code = 'JUN'
    
    def get_queryset(self):
        try:
            match_type = TypeMatch.objects.get(code='JUN', is_active=True)
            return Match.objects.filter(
                type_match=match_type,
                status='completed'
            ).select_related('type_match', 'categorie', 'referee').order_by('-match_date', '-match_time')
        except TypeMatch.DoesNotExist:
            return Match.objects.none()

class CoupeTunisieMatchesView(CompetitionMatchesView):
    """Récupérer les matchs sifflés de Coupe de Tunisie"""
    type_code = 'CT'
    
    def get_queryset(self):
        try:
            match_type = TypeMatch.objects.get(code='CT', is_active=True)
            return Match.objects.filter(
                type_match=match_type,
                status='completed'
            ).select_related('type_match', 'categorie', 'referee').order_by('-match_date', '-match_time')
        except TypeMatch.DoesNotExist:
            return Match.objects.none()


# ===== EXCUSES D'ARBITRES =====
class ExcuseArbitreListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des excuses d'arbitres"""
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ExcuseArbitreCreateSerializer
        return ExcuseArbitreListSerializer
    
    def get_queryset(self):
        """Retourner toutes les excuses d'arbitres"""
        return ExcuseArbitre.objects.all().order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """Lister toutes les excuses d'arbitres"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'message': f'{queryset.count()} excuse(s) trouvée(s)',
            'excuses': serializer.data
        })
    
    def create(self, request, *args, **kwargs):
        """Créer une nouvelle excuse d'arbitre"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            excuse = serializer.save()
            return Response({
                'success': True,
                'message': 'Excuse créée avec succès',
                'excuse': ExcuseArbitreSerializer(excuse).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Erreur lors de la création de l\'excuse',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ExcuseArbitreDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour consulter, modifier et supprimer une excuse d'arbitre"""
    serializer_class = ExcuseArbitreSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Retourner toutes les excuses d'arbitres"""
        return ExcuseArbitre.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        """Récupérer une excuse spécifique"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'success': True,
            'message': 'Excuse récupérée avec succès',
            'excuse': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        """Modifier une excuse"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            excuse = serializer.save()
            return Response({
                'success': True,
                'message': 'Excuse modifiée avec succès',
                'excuse': serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Erreur lors de la modification de l\'excuse',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Supprimer une excuse"""
        instance = self.get_object()
        instance.delete()
        
        return Response({
            'success': True,
            'message': 'Excuse supprimée avec succès'
        }, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def excuses_arbitre_statistics(request):
    """Statistiques des excuses d'arbitres"""
    total_excuses = ExcuseArbitre.objects.count()
    
    # Excuses par mois (6 derniers mois)
    from datetime import datetime, timedelta
    six_months_ago = datetime.now() - timedelta(days=180)
    recent_excuses = ExcuseArbitre.objects.filter(created_at__gte=six_months_ago).count()
    
    # Excuses actives (en cours)
    today = timezone.now().date()
    active_excuses = ExcuseArbitre.objects.filter(
        date_debut__lte=today,
        date_fin__gte=today
    ).count()
    
    return Response({
        'success': True,
        'statistics': {
            'total_excuses': total_excuses,
            'recent_excuses': recent_excuses,
            'active_excuses': active_excuses
        }
    })


def excuses_passees_par_date(request):
    """API pour voir les excuses passées par date"""
    from datetime import date
    from django.http import JsonResponse
    
    # Récupérer la date depuis les paramètres de requête
    date_param = request.GET.get('date')
    
    if not date_param:
        return JsonResponse({
            'success': False,
            'message': 'Paramètre date requis (format: YYYY-MM-DD)'
        }, status=400)
    
    try:
        # Convertir la date
        target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Format de date invalide. Utilisez YYYY-MM-DD'
        }, status=400)
    
    # Récupérer les excuses passées (date_fin < date cible)
    excuses_passees = ExcuseArbitre.objects.filter(
        date_fin__lt=target_date
    ).order_by('-date_fin')
    
    serializer = ExcuseArbitreSerializer(excuses_passees, many=True)
    
    return JsonResponse({
        'success': True,
        'message': f'{excuses_passees.count()} excuse(s) passée(s) trouvée(s) pour le {target_date}',
        'date_cible': target_date.strftime('%Y-%m-%d'),
        'excuses_passees': serializer.data
    })


def excuses_en_cours_par_date(request):
    """API pour voir les excuses en cours par date"""
    from datetime import date
    from django.http import JsonResponse
    
    # Récupérer la date depuis les paramètres de requête
    date_param = request.GET.get('date')
    
    if not date_param:
        return JsonResponse({
            'success': False,
            'message': 'Paramètre date requis (format: YYYY-MM-DD)'
        }, status=400)
    
    try:
        # Convertir la date
        target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Format de date invalide. Utilisez YYYY-MM-DD'
        }, status=400)
    
    # Récupérer les excuses en cours (date_debut <= date cible <= date_fin)
    excuses_en_cours = ExcuseArbitre.objects.filter(
        date_debut__lte=target_date,
        date_fin__gte=target_date
    ).order_by('-created_at')
    
    serializer = ExcuseArbitreSerializer(excuses_en_cours, many=True)
    
    return JsonResponse({
        'success': True,
        'message': f'{excuses_en_cours.count()} excuse(s) en cours trouvée(s) pour le {target_date}',
        'date_cible': target_date.strftime('%Y-%m-%d'),
        'excuses_en_cours': serializer.data
    })


def excuses_a_venir_par_date(request):
    """API pour voir les excuses à venir par date"""
    from datetime import date
    from django.http import JsonResponse
    
    # Récupérer la date depuis les paramètres de requête
    date_param = request.GET.get('date')
    
    if not date_param:
        return JsonResponse({
            'success': False,
            'message': 'Paramètre date requis (format: YYYY-MM-DD)'
        }, status=400)
    
    try:
        # Convertir la date
        target_date = datetime.strptime(date_param, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Format de date invalide. Utilisez YYYY-MM-DD'
        }, status=400)
    
    # Récupérer les excuses à venir (date_debut > date cible)
    excuses_a_venir = ExcuseArbitre.objects.filter(
        date_debut__gt=target_date
    ).order_by('date_debut')
    
    serializer = ExcuseArbitreSerializer(excuses_a_venir, many=True)
    
    return JsonResponse({
        'success': True,
        'message': f'{excuses_a_venir.count()} excuse(s) à venir trouvée(s) pour le {target_date}',
        'date_cible': target_date.strftime('%Y-%m-%d'),
        'excuses_a_venir': serializer.data
    })


# ==================== VUES POUR LA TARIFICATION DES MATCHS ====================

class TarificationMatchListView(generics.ListAPIView):
    """Vue pour lister toutes les tarifications de matchs"""
    queryset = TarificationMatch.objects.all()
    serializer_class = TarificationMatchListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Filtrer les tarifications selon les paramètres"""
        queryset = TarificationMatch.objects.all()
        
        # Filtres optionnels
        competition = self.request.query_params.get('competition')
        division = self.request.query_params.get('division')
        type_match = self.request.query_params.get('type_match')
        role = self.request.query_params.get('role')
        is_active = self.request.query_params.get('is_active')
        
        if competition:
            queryset = queryset.filter(competition=competition)
        if division:
            queryset = queryset.filter(division=division)
        if type_match:
            queryset = queryset.filter(type_match=type_match)
        if role:
            queryset = queryset.filter(role=role)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('competition', 'division', 'type_match', 'role')


class TarificationMatchDetailView(generics.RetrieveAPIView):
    """Vue pour récupérer une tarification spécifique"""
    queryset = TarificationMatch.objects.all()
    serializer_class = TarificationMatchSerializer
    permission_classes = [permissions.AllowAny]


class TarificationMatchCreateView(generics.CreateAPIView):
    """Vue pour créer une nouvelle tarification"""
    queryset = TarificationMatch.objects.all()
    serializer_class = TarificationMatchCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """Créer une nouvelle tarification"""
        serializer.save()


class TarificationMatchUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour modifier/supprimer une tarification"""
    queryset = TarificationMatch.objects.all()
    serializer_class = TarificationMatchUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Retourner le bon serializer selon l'action"""
        if self.request.method in ['PUT', 'PATCH']:
            return TarificationMatchUpdateSerializer
        return TarificationMatchSerializer


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def tarification_by_competition(request, competition):
    """Récupérer toutes les tarifications d'une compétition"""
    try:
        tarifications = TarificationMatch.objects.filter(
            competition=competition,
            is_active=True
        ).order_by('division', 'type_match', 'role')
        
        serializer = TarificationMatchListSerializer(tarifications, many=True)
        
        return Response({
            'success': True,
            'message': f'Tarifications trouvées pour {competition}',
            'competition': competition,
            'count': tarifications.count(),
            'tarifications': serializer.data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Erreur lors de la récupération des tarifications: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def tarification_by_type_match(request, competition, type_match):
    """Récupérer les tarifications d'un type de match spécifique"""
    try:
        tarifications = TarificationMatch.objects.filter(
            competition=competition,
            type_match=type_match,
            is_active=True
        ).order_by('division', 'role')
        
        serializer = TarificationMatchListSerializer(tarifications, many=True)
        
        return Response({
            'success': True,
            'message': f'Tarifications trouvées pour {competition} - {type_match}',
            'competition': competition,
            'type_match': type_match,
            'count': tarifications.count(),
            'tarifications': serializer.data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Erreur lors de la récupération des tarifications: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def tarification_by_role(request, competition, type_match, role):
    """Récupérer la tarification d'un rôle spécifique"""
    try:
        tarification = TarificationMatch.objects.get(
            competition=competition,
            type_match=type_match,
            role=role,
            is_active=True
        )
        
        serializer = TarificationMatchSerializer(tarification)
        
        return Response({
            'success': True,
            'message': 'Tarification trouvée',
            'tarification': serializer.data
        })
        
    except TarificationMatch.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Tarification non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Erreur lors de la récupération de la tarification: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

