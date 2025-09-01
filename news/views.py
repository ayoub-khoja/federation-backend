from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from django.core.paginator import Paginator
from django.db.models import Q
from .models import News
from .serializers import NewsSerializer, NewsCreateSerializer, NewsUpdateSerializer


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Accessible à tous pour la lecture
def news_list(request):
    """Liste des actualités publiées"""
    try:
        # Paramètres de requête
        page = int(request.GET.get('page', 1))
        search = request.GET.get('search', '')
        language = request.GET.get('language', 'fr')  # fr ou ar
        featured_only = request.GET.get('featured', 'false').lower() == 'true'
        
        # Construire la requête
        queryset = News.objects.filter(is_published=True)
        
        if featured_only:
            queryset = queryset.filter(is_featured=True)
        
        if search:
            if language == 'ar':
                queryset = queryset.filter(
                    Q(title_ar__icontains=search) | Q(content_ar__icontains=search)
                )
            else:
                queryset = queryset.filter(
                    Q(title_fr__icontains=search) | Q(content_fr__icontains=search)
                )
        
        # Pagination
        paginator = Paginator(queryset, 10)
        page_obj = paginator.get_page(page)
        
        # Sérializer
        serializer = NewsSerializer(page_obj, many=True)
        
        return Response({
            'results': serializer.data,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous()
        })
        
    except Exception as e:
        return Response({
            'detail': f'Erreur lors de la récupération des actualités: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def admin_news_list(request):
    """Liste des actualités pour l'administration"""
    # Valider l'authentification JWT
    from accounts.views import validate_jwt_admin
    admin_user, error_message = validate_jwt_admin(request)
    if not admin_user:
        return Response({'detail': error_message}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Paramètres de requête
        page = int(request.GET.get('page', 1))
        search = request.GET.get('search', '')
        
        # Construire la requête (toutes les actualités pour l'admin)
        queryset = News.objects.all()
        
        if search:
            queryset = queryset.filter(
                Q(title_fr__icontains=search) | 
                Q(title_ar__icontains=search) |
                Q(content_fr__icontains=search) |
                Q(content_ar__icontains=search)
            )
        
        # Pagination
        paginator = Paginator(queryset, 20)
        page_obj = paginator.get_page(page)
        
        # Sérializer
        serializer = NewsSerializer(page_obj, many=True)
        
        return Response({
            'results': serializer.data,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page
        })
        
    except Exception as e:
        return Response({
            'detail': f'Erreur lors de la récupération des actualités: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_news(request):
    """Créer une nouvelle actualité"""
    # Valider l'authentification JWT
    from accounts.views import validate_jwt_admin
    admin_user, error_message = validate_jwt_admin(request)
    if not admin_user:
        return Response({'detail': error_message}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        serializer = NewsCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Créer l'actualité sans l'auteur d'abord
            news = serializer.save()
            
            # Assigner l'auteur avec le nouveau système GenericForeignKey
            from django.contrib.contenttypes.models import ContentType
            news.content_type = ContentType.objects.get_for_model(admin_user)
            news.object_id = admin_user.id
            news.save()
            
            # Retourner l'actualité créée
            response_serializer = NewsSerializer(news)
            return Response({
                'message': 'Actualité créée avec succès',
                'news': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'detail': 'Données invalides',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'detail': f'Erreur lors de la création: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def news_detail(request, news_id):
    """Détail d'une actualité"""
    try:
        news = News.objects.get(id=news_id, is_published=True)
        serializer = NewsSerializer(news)
        return Response(serializer.data)
        
    except News.DoesNotExist:
        return Response({
            'detail': 'Actualité non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_news(request, news_id):
    """Mettre à jour une actualité"""
    # Valider l'authentification JWT
    from accounts.views import validate_jwt_admin
    admin_user, error_message = validate_jwt_admin(request)
    if not admin_user:
        return Response({'detail': error_message}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        news = News.objects.get(id=news_id)
        
        # Les admins peuvent modifier toutes les actualités
        serializer = NewsUpdateSerializer(news, data=request.data, partial=True)
        if serializer.is_valid():
            updated_news = serializer.save()
            response_serializer = NewsSerializer(updated_news)
            return Response({
                'message': 'Actualité mise à jour avec succès',
                'news': response_serializer.data
            })
        
        return Response({
            'detail': 'Données invalides',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except News.DoesNotExist:
        return Response({
            'detail': 'Actualité non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_news(request, news_id):
    """Supprimer une actualité"""
    # Valider l'authentification JWT
    from accounts.views import validate_jwt_admin
    admin_user, error_message = validate_jwt_admin(request)
    if not admin_user:
        return Response({'detail': error_message}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        news = News.objects.get(id=news_id)
        
        # Les admins peuvent supprimer toutes les actualités
        news.delete()
        return Response({
            'message': 'Actualité supprimée avec succès'
        })
        
    except News.DoesNotExist:
        return Response({
            'detail': 'Actualité non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_featured(request, news_id):
    """Basculer le statut "à la une" d'une actualité"""
    # Valider l'authentification JWT
    from accounts.views import validate_jwt_admin
    admin_user, error_message = validate_jwt_admin(request)
    if not admin_user:
        return Response({'detail': error_message}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        news = News.objects.get(id=news_id)
        news.is_featured = not news.is_featured
        news.save()
        
        serializer = NewsSerializer(news)
        return Response({
            'message': f'Actualité {"mise à la une" if news.is_featured else "retirée de la une"}',
            'news': serializer.data
        })
        
    except News.DoesNotExist:
        return Response({
            'detail': 'Actualité non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)