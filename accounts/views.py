"""
Vues pour l'API des utilisateurs du système d'arbitrage
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Arbitre, Commissaire, Admin, LigueArbitrage
from .serializers import (
    ArbitreRegistrationSerializer, ArbitreProfileSerializer, ArbitreUpdateSerializer,
    ArbitreLoginSerializer,
    CommissaireRegistrationSerializer, CommissaireProfileSerializer, CommissaireUpdateSerializer,
    CommissaireLoginSerializer,
    AdminRegistrationSerializer, AdminProfileSerializer, AdminUpdateSerializer,
    AdminLoginSerializer,
    ChangePasswordSerializer, LigueArbitrageSerializer,
    UnifiedLoginSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import PushSubscription
from django.utils import timezone

# ============================================================================
# FONCTIONS HELPER
# ============================================================================

def normalize_phone_number(phone_number):
    """
    Normalise un numéro de téléphone tunisien
    """
    # Supprimer tous les espaces et caractères spéciaux
    phone = ''.join(filter(str.isdigit, phone_number))
    
    # Si le numéro commence par 216, le garder tel quel
    if phone.startswith('216'):
        return phone
    # Si le numéro commence par 0, remplacer par 216
    elif phone.startswith('0'):
        return '216' + phone[1:]
    # Si le numéro a 8 chiffres, ajouter 216
    elif len(phone) == 8:
        return '216' + phone
    # Sinon, retourner tel quel
    else:
        return phone

def check_phone_number_exists(phone_number):
    """
    Vérifie si un numéro de téléphone existe déjà dans la base de données
    Retourne (exists, user_type, user_info)
    """
    normalized_phone = normalize_phone_number(phone_number)
    
    # Vérifier dans Arbitre
    try:
        arbitre = Arbitre.objects.get(phone_number=normalized_phone)
        return True, 'arbitre', {
            'id': arbitre.id,
            'full_name': arbitre.get_full_name(),
            'grade': arbitre.grade,
            'ligue': arbitre.ligue.nom if arbitre.ligue else None,
            'is_active': arbitre.is_active
        }
    except Arbitre.DoesNotExist:
        pass
    
    # Vérifier dans Commissaire
    try:
        commissaire = Commissaire.objects.get(phone_number=normalized_phone)
        return True, 'commissaire', {
            'id': commissaire.id,
            'full_name': commissaire.get_full_name(),
            'grade': commissaire.grade,
            'specialite': commissaire.specialite,
            'ligue': commissaire.ligue.nom if commissaire.ligue else None,
            'is_active': commissaire.is_active
        }
    except Commissaire.DoesNotExist:
        pass
    
    # Vérifier dans Admin
    try:
        admin = Admin.objects.get(phone_number=normalized_phone)
        return True, 'admin', {
            'id': admin.id,
            'full_name': admin.get_full_name(),
            'user_type': admin.user_type,
            'department': admin.department,
            'position': admin.position,
            'is_active': admin.is_active
        }
    except Admin.DoesNotExist:
        pass
    
    return False, None, None

def validate_jwt_admin(request):
    """
    Valide l'authentification JWT et retourne l'utilisateur admin
    """
    try:
        # Récupérer le token depuis les headers
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            # Valider le token JWT
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)
            user_id = validated_token['user_id']
            
            # Récupérer l'utilisateur Admin
            try:
                admin_user = Admin.objects.get(id=user_id, is_active=True)
                if not admin_user.is_staff and not admin_user.is_superuser:
                    return None, 'Accès non autorisé - Permissions insuffisantes'
                return admin_user, None
                    
            except Admin.DoesNotExist:
                return None, 'Utilisateur admin non trouvé'
        else:
            return None, 'Token d\'authentification manquant'
            
    except Exception as e:
        print(f"❌ Erreur lors de la validation JWT: {e}")
        return None, 'Token d\'authentification invalide'

# ============================================================================
# VÉRIFICATION DE NUMÉRO DE TÉLÉPHONE
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_phone_number(request):
    """
    Vérifie si un numéro de téléphone existe déjà dans la base de données
    """
    phone_number = request.data.get('phone_number')
    
    if not phone_number:
        return Response({
            'success': False,
            'message': 'Le numéro de téléphone est requis',
            'error_code': 'PHONE_REQUIRED'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Normaliser le numéro
        normalized_phone = normalize_phone_number(phone_number)
        
        # Vérifier l'existence
        exists, user_type, user_info = check_phone_number_exists(phone_number)
        
        if exists:
            return Response({
                'success': True,
                'exists': True,
                'message': f'Ce numéro de téléphone est déjà utilisé par un {user_type}',
                'user_type': user_type,
                'user_info': user_info,
                'normalized_phone': normalized_phone,
                'error_code': 'PHONE_EXISTS'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': True,
                'exists': False,
                'message': 'Ce numéro de téléphone est disponible',
                'normalized_phone': normalized_phone,
                'error_code': 'PHONE_AVAILABLE'
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Erreur lors de la vérification du numéro',
            'error': str(e),
            'error_code': 'VERIFICATION_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============================================================================
# AUTHENTIFICATION UNIFIÉE (pour mobile)
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def unified_login(request):
    """Connexion unifiée pour tous les types d'utilisateurs (mobile)"""
    serializer = UnifiedLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        user_type = serializer.validated_data['user_type']
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        
        # Préparer la réponse selon le type d'utilisateur
        if user_type == 'arbitre':
            user_data = {
                'id': user.id,
                'phone_number': user.phone_number,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
                'user_type': 'arbitre',
                'grade': user.grade,
                'league': user.ligue.nom if user.ligue else None,
                'email': user.email
            }
        elif user_type == 'commissaire':
            user_data = {
                'id': user.id,
                'phone_number': user.phone_number,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
                'user_type': 'commissaire',
                'grade': user.grade,
                'league': user.ligue.nom if user.ligue else None,
                'email': user.email
            }
        elif user_type == 'admin':
            user_data = {
                'id': user.id,
                'phone_number': user.phone_number,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
                'user_type': 'admin',
                'grade': None,
                'league': None,
                'email': user.email
            }
        else:
            user_data = {
                'id': user.id,
                'phone_number': user.phone_number,
                'first_name': getattr(user, 'first_name', ''),
                'last_name': getattr(user, 'last_name', ''),
                'full_name': getattr(user, 'get_full_name', lambda: '')() or f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip(),
                'user_type': user_type,
                'grade': getattr(user, 'grade', None),
                'league': getattr(user.ligue, 'nom', None) if hasattr(user, 'ligue') and user.ligue else None,
                'email': getattr(user, 'email', None)
            }
        
        return Response({
            'success': True,
            'message': f'Connexion réussie en tant que {user_type}',
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            },
            'user': user_data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': 'Échec de la connexion',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def unified_logout(request):
    """Déconnexion unifiée (mobile)"""
    try:
        # Pour l'instant, on ne fait que valider que la requête est bien formée
        # Le frontend se chargera de supprimer les tokens
        return Response({
            'success': True,
            'message': 'Déconnexion réussie'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Erreur lors de la déconnexion',
            'errors': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

# ============================================================================
# VUES POUR LES ARBITRES
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def arbitre_register(request):
    """Inscription d'un nouvel arbitre"""
    phone_number = request.data.get('phone_number')
    
    # Vérifier d'abord si le numéro existe
    if phone_number:
        exists, user_type, user_info = check_phone_number_exists(phone_number)
        if exists:
            return Response({
                'success': False,
                'message': f'Ce numéro de téléphone est déjà utilisé par un {user_type}',
                'error_code': 'PHONE_EXISTS',
                'user_type': user_type,
                'user_info': user_info
            }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = ArbitreRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        arbitre = serializer.save()
        
        # Sérialiser les données complètes de l'arbitre créé
        from .serializers import ArbitreProfileSerializer
        arbitre_data = ArbitreProfileSerializer(arbitre).data
        
        return Response({
            'success': True,
            'message': 'Compte arbitre créé avec succès',
            'arbitre': arbitre_data
        }, status=status.HTTP_201_CREATED)
    
    # Améliorer la gestion des erreurs
    error_details = {}
    for field, errors in serializer.errors.items():
        if isinstance(errors, list):
            error_details[field] = errors[0] if errors else "Erreur de validation"
        else:
            error_details[field] = str(errors)
    
    return Response({
        'success': False,
        'message': 'Erreur de validation des données',
        'errors': error_details
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def arbitre_login(request):
    """Connexion d'un arbitre"""
    serializer = ArbitreLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'success': True,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'phone_number': user.phone_number,
                'full_name': user.get_full_name(),
                'user_type': 'arbitre',
                'grade': user.grade,
                'ligue': user.ligue.nom if user.ligue else None
            }
        })
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def arbitre_profile(request):
    """Récupération du profil complet de l'arbitre connecté"""
    # Debug: Afficher les informations de l'utilisateur
    print(f"🔍 DEBUG - request.user: {request.user}")
    print(f"🔍 DEBUG - type(request.user): {type(request.user)}")
    print(f"🔍 DEBUG - request.user.is_authenticated: {request.user.is_authenticated}")
    print(f"🔍 DEBUG - request.user.id: {getattr(request.user, 'id', 'N/A')}")
    
    if not isinstance(request.user, Arbitre):
        print(f"❌ DEBUG - L'utilisateur n'est pas un Arbitre, c'est un: {type(request.user)}")
        return Response({'detail': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ArbitreProfileSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def test_auth(request):
    """Vue de test pour diagnostiquer l'authentification JWT"""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    print(f"🔍 DEBUG - Auth header: {auth_header}")
    
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        print(f"🔍 DEBUG - Token extrait: {token[:20]}...")
        
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            validated_token = AccessToken(token)
            user_id = validated_token['user_id']
            print(f"🔍 DEBUG - User ID from token: {user_id}")
            
            # Essayer de récupérer l'utilisateur
            try:
                user = Arbitre.objects.get(id=user_id)
                print(f"🔍 DEBUG - Arbitre trouvé: {user.first_name} {user.last_name}")
                return Response({
                    'success': True,
                    'message': 'Token valide, utilisateur trouvé',
                    'user_id': user_id,
                    'user_name': f"{user.first_name} {user.last_name}"
                })
            except Arbitre.DoesNotExist:
                print(f"❌ DEBUG - Arbitre avec ID {user_id} non trouvé")
                return Response({
                    'success': False,
                    'message': f'Arbitre avec ID {user_id} non trouvé',
                    'user_id': user_id
                }, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            print(f"❌ DEBUG - Erreur lors de la validation du token: {e}")
            return Response({
                'success': False,
                'message': f'Erreur de validation du token: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    else:
        print("❌ DEBUG - Pas de header Authorization")
        return Response({
            'success': False,
            'message': 'Pas de header Authorization'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def push_subscribe(request):
    """Abonnement aux notifications push"""
    try:
        endpoint = request.data.get('endpoint')
        p256dh = request.data.get('p256dh')
        auth = request.data.get('auth')
        
        if not all([endpoint, p256dh, auth]):
            return Response({
                'error': 'Données d\'abonnement manquantes'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer ou mettre à jour l'abonnement
        subscription, created = PushSubscription.objects.get_or_create(
            arbitre=request.user,
            endpoint=endpoint,
            defaults={
                'p256dh': p256dh,
                'auth': auth,
                'is_active': True
            }
        )
        
        if not created:
            # Mettre à jour l'abonnement existant
            subscription.p256dh = p256dh
            subscription.auth = auth
            subscription.is_active = True
            subscription.save()
        
        return Response({
            'success': True,
            'message': 'Abonnement aux notifications créé avec succès'
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def push_unsubscribe(request):
    """Désabonnement des notifications push"""
    try:
        endpoint = request.data.get('endpoint')
        
        if not endpoint:
            return Response({
                'error': 'Endpoint manquant'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Désactiver l'abonnement
        PushSubscription.objects.filter(
            arbitre=request.user,
            endpoint=endpoint
        ).update(is_active=False)
        
        return Response({
            'success': True,
            'message': 'Désabonnement réussi'
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def arbitre_update_profile(request):
    """Mise à jour du profil de l'arbitre connecté"""
    if not isinstance(request.user, Arbitre):
        return Response({'detail': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ArbitreUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Profil mis à jour avec succès'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ============================================================================
# VUES POUR LES COMMISSAIRES
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def commissaire_register(request):
    """Inscription d'un nouveau commissaire"""
    phone_number = request.data.get('phone_number')
    
    # Vérifier d'abord si le numéro existe
    if phone_number:
        exists, user_type, user_info = check_phone_number_exists(phone_number)
        if exists:
            return Response({
                'success': False,
                'message': f'Ce numéro de téléphone est déjà utilisé par un {user_type}',
                'error_code': 'PHONE_EXISTS',
                'user_type': user_type,
                'user_info': user_info
            }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = CommissaireRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        commissaire = serializer.save()
        return Response({
            'success': True,
            'message': 'Compte commissaire créé avec succès',
            'commissaire_id': commissaire.id
        }, status=status.HTTP_201_CREATED)
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def commissaire_login(request):
    """Connexion d'un commissaire"""
    serializer = CommissaireLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'success': True,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'phone_number': user.phone_number,
                'full_name': user.get_full_name(),
                'user_type': 'commissaire',
                'specialite': user.specialite,
                'grade': user.grade,
                'ligue': user.ligue.nom if user.ligue else None
            }
        })
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def commissaire_profile(request):
    """Récupération du profil complet du commissaire connecté"""
    if not isinstance(request.user, Commissaire):
        return Response({'detail': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = CommissaireProfileSerializer(request.user)
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def commissaire_update_profile(request):
    """Mise à jour du profil du commissaire connecté"""
    if not isinstance(request.user, Commissaire):
        return Response({'detail': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = CommissaireUpdateSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Profil mis à jour avec succès'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ============================================================================
# VUES POUR LES ADMINISTRATEURS
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def admin_register(request):
    """Inscription d'un nouvel administrateur"""
    phone_number = request.data.get('phone_number')
    
    # Vérifier d'abord si le numéro existe
    if phone_number:
        exists, user_type, user_info = check_phone_number_exists(phone_number)
        if exists:
            return Response({
                'success': False,
                'message': f'Ce numéro de téléphone est déjà utilisé par un {user_type}',
                'error_code': 'PHONE_EXISTS',
                'user_type': user_type,
                'user_info': user_info
            }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = AdminRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        admin = serializer.save()
        return Response({
            'success': True,
            'message': 'Compte administrateur créé avec succès',
            'admin_id': admin.id
        }, status=status.HTTP_201_CREATED)
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def admin_login(request):
    """Connexion d'un administrateur"""
    serializer = AdminLoginSerializer(data=request.data)
    if serializer.is_valid():
        user_data = serializer.validated_data['user']
        # Récupérer l'objet Admin original pour le token
        admin_obj = Admin.objects.get(id=user_data['id'])
        refresh = RefreshToken.for_user(admin_obj)
        return Response({
            'success': True,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data  # Utiliser directement les données du serializer
        })
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def admin_profile(request):
    """Récupération du profil complet de l'administrateur connecté"""
    # Valider l'authentification JWT
    admin_user, error_message = validate_jwt_admin(request)
    if not admin_user:
        return Response({'detail': error_message}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = AdminProfileSerializer(admin_user)
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def admin_update_profile(request):
    """Mise à jour du profil de l'administrateur connecté"""
    # Valider l'authentification JWT
    admin_user, error_message = validate_jwt_admin(request)
    if not admin_user:
        return Response({'detail': error_message}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = AdminUpdateSerializer(admin_user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Profil mis à jour avec succès'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ============================================================================
# VUES COMMUNES
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    """Changement de mot de passe pour tous les types d'utilisateurs"""
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Mot de passe modifié avec succès'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def ligues_list(request):
    """Liste des ligues d'arbitrage actives"""
    ligues = LigueArbitrage.objects.filter(is_active=True).order_by('ordre', 'nom')
    serializer = LigueArbitrageSerializer(ligues, many=True)
    return Response({
        'success': True,
        'ligues': serializer.data,
        'count': len(serializer.data)
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def ligue_create(request):
    """Créer une nouvelle ligue d'arbitrage"""
    # Valider l'authentification JWT
    admin_user, error_message = validate_jwt_admin(request)
    if not admin_user:
        return Response({'detail': error_message}, status=status.HTTP_403_FORBIDDEN)
    
    print(f"✅ Admin trouvé via JWT: {admin_user.get_full_name()}")
    
    serializer = LigueArbitrageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Ligue créée avec succès',
            'ligue': serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def ligue_detail(request, ligue_id):
    """Détails d'une ligue d'arbitrage"""
    try:
        ligue = LigueArbitrage.objects.get(id=ligue_id, is_active=True)
        serializer = LigueArbitrageSerializer(ligue)
        return Response({
            'success': True,
            'ligue': serializer.data
        })
    except LigueArbitrage.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Ligue non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def ligue_update(request, ligue_id):
    """Mettre à jour une ligue d'arbitrage"""
    # Valider l'authentification JWT
    admin_user, error_message = validate_jwt_admin(request)
    if not admin_user:
        return Response({'detail': error_message}, status=status.HTTP_403_FORBIDDEN)
    
    print(f"✅ Admin trouvé via JWT pour mise à jour: {admin_user.get_full_name()}")
    
    try:
        ligue = LigueArbitrage.objects.get(id=ligue_id)
        serializer = LigueArbitrageSerializer(ligue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Ligue mise à jour avec succès',
                'ligue': serializer.data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except LigueArbitrage.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Ligue non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def ligue_delete(request, ligue_id):
    """Supprimer une ligue d'arbitrage"""
    # Valider l'authentification JWT
    admin_user, error_message = validate_jwt_admin(request)
    if not admin_user:
        return Response({'detail': error_message}, status=status.HTTP_403_FORBIDDEN)
    
    print(f"✅ Admin trouvé via JWT pour suppression: {admin_user.get_full_name()}")
    
    try:
        ligue = LigueArbitrage.objects.get(id=ligue_id)
        ligue.delete()
        return Response({
            'success': True,
            'message': 'Ligue supprimée avec succès'
        })
    except LigueArbitrage.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Ligue non trouvée'
        }, status=status.HTTP_404_NOT_FOUND)

# ============================================================================
# VUES D'ADMINISTRATION
# ============================================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def users_list(request):
    """Liste des utilisateurs pour l'administration"""
    # Valider l'authentification JWT
    admin_user, error_message = validate_jwt_admin(request)
    if not admin_user:
        return Response({'detail': error_message}, status=status.HTTP_403_FORBIDDEN)
    
    user_type = request.GET.get('type', 'all')
    search = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    
    if user_type == 'arbitres':
        users = Arbitre.objects.all().select_related('ligue')
        user_class = Arbitre
    elif user_type == 'commissaires':
        users = Commissaire.objects.all().select_related('ligue')
        user_class = Commissaire
    elif user_type == 'admins':
        users = Admin.objects.all()
        user_class = Admin
    else:
        # Combiner tous les types
        arbitres = Arbitre.objects.all().select_related('ligue')
        commissaires = Commissaire.objects.all().select_related('ligue')
        admins = Admin.objects.all()
        users = list(arbitres) + list(commissaires) + list(admins)
        user_class = None
    
    if search and user_class:
        users = users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(phone_number__icontains=search) |
            Q(email__icontains=search)
        )
    
    if user_class:
        users = users.order_by('-date_joined')
        paginator = Paginator(users, 20)
        page_obj = paginator.get_page(page)
        
        results = []
        for user in page_obj:
            user_data = {
                'id': user.id,
                'phone_number': user.phone_number,
                'full_name': user.get_full_name(),
                'email': user.email,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat(),
                'user_type': user_type[:-1] if user_type.endswith('s') else user_type
            }
            
            if hasattr(user, 'grade'):
                user_data['grade'] = user.grade
            if hasattr(user, 'ligue'):
                user_data['ligue_nom'] = user.ligue.nom if user.ligue else None
            if hasattr(user, 'specialite'):
                user_data['specialite'] = user.specialite
            if hasattr(user, 'user_type'):
                user_data['admin_type'] = user.get_user_type_display()
            if hasattr(user, 'department'):
                user_data['department'] = user.department
            if hasattr(user, 'position'):
                user_data['position'] = user.position
            
            results.append(user_data)
        
        return Response({
            'results': results,
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page
        })
    
    return Response({'detail': 'Type d\'utilisateur non spécifié'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def admin_stats(request):
    """Statistiques pour l'administration"""
    if not isinstance(request.user, Admin):
        return Response({'detail': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)
    
    stats = {
        'total_arbitres': Arbitre.objects.count(),
        'arbitres_actifs': Arbitre.objects.filter(is_active=True).count(),
        'total_commissaires': Commissaire.objects.count(),
        'commissaires_actifs': Commissaire.objects.filter(is_active=True).count(),
        'total_admins': Admin.objects.count(),
        'admins_actifs': Admin.objects.filter(is_active=True).count(),
        'total_ligues': LigueArbitrage.objects.filter(is_active=True).count(),
    }
    
    # Ajouter les stats de matches si l'app matches est disponible
    try:
        from matches.models import Match
        stats['total_matches'] = Match.objects.count()
        # Matches du mois actuel
        from datetime import datetime
        current_month = datetime.now().month
        current_year = datetime.now().year
        stats['matches_ce_mois'] = Match.objects.filter(
            match_date__month=current_month,
            match_date__year=current_year
        ).count()
    except ImportError:
        stats['total_matches'] = 0
        stats['matches_ce_mois'] = 0
    
    return Response(stats)

# ============================================================================
# NOTIFICATIONS PUSH
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def push_subscribe(request):
    """Abonnement aux notifications push"""
    try:
        # Vérifier que l'utilisateur est un arbitre
        if not isinstance(request.user, Arbitre):
            return Response(
                {'error': 'Seuls les arbitres peuvent s\'abonner aux notifications push'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        endpoint = request.data.get('endpoint')
        p256dh = request.data.get('p256dh')
        auth = request.data.get('auth')
        
        if not all([endpoint, p256dh, auth]):
            return Response({
                'error': 'Données d\'abonnement manquantes'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer ou mettre à jour l'abonnement
        subscription, created = PushSubscription.objects.get_or_create(
            arbitre=request.user,
            endpoint=endpoint,
            defaults={
                'p256dh': p256dh,
                'auth': auth,
                'is_active': True
            }
        )
        
        if not created:
            # Mettre à jour l'abonnement existant
            subscription.p256dh = p256dh
            subscription.auth = auth
            subscription.is_active = True
            subscription.save()
        
        return Response({
            'success': True,
            'message': 'Abonnement aux notifications créé avec succès'
        })
        
    except Exception as e:
        print(f"❌ Erreur lors de l'abonnement push: {e}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def push_unsubscribe(request):
    """Désabonnement des notifications push"""
    try:
        # Vérifier que l'utilisateur est un arbitre
        if not isinstance(request.user, Arbitre):
            return Response(
                {'error': 'Seuls les arbitres peuvent se désabonner des notifications push'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        endpoint = request.data.get('endpoint')
        
        if not endpoint:
            return Response({
                'error': 'Endpoint manquant'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Désactiver l'abonnement
        PushSubscription.objects.filter(
            arbitre=request.user,
            endpoint=endpoint
        ).update(is_active=False)
        
        return Response({
            'success': True,
            'message': 'Désabonnement réussi'
        })
        
    except Exception as e:
        print(f"❌ Erreur lors du désabonnement push: {e}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def subscribe_push(request):
    """S'abonner aux notifications push"""
    try:
        # Vérifier que l'utilisateur est un arbitre
        if not isinstance(request.user, Arbitre):
            return Response(
                {'detail': 'Seuls les arbitres peuvent s\'abonner aux notifications push'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Récupérer les données d'abonnement
        endpoint = request.data.get('endpoint')
        p256dh = request.data.get('keys', {}).get('p256dh')
        auth = request.data.get('keys', {}).get('auth')
        
        if not all([endpoint, p256dh, auth]):
            return Response(
                {'detail': 'Données d\'abonnement incomplètes'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Créer ou mettre à jour l'abonnement
        subscription, created = PushSubscription.objects.update_or_create(
            arbitre=request.user,
            endpoint=endpoint,
            defaults={
                'p256dh': p256dh,
                'auth': auth,
                'is_active': True
            }
        )
        
        return Response({
            'detail': 'Abonnement push créé avec succès' if created else 'Abonnement push mis à jour',
            'subscription_id': subscription.id
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ Erreur lors de l'abonnement push: {e}")
        return Response(
            {'detail': 'Erreur lors de l\'abonnement aux notifications push'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def unsubscribe_push(request):
    """Se désabonner des notifications push"""
    try:
        # Vérifier que l'utilisateur est un arbitre
        if not isinstance(request.user, Arbitre):
            return Response(
                {'detail': 'Seuls les arbitres peuvent se désabonner des notifications push'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        endpoint = request.data.get('endpoint')
        if not endpoint:
            return Response(
                {'detail': 'Endpoint requis pour le désabonnement'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Désactiver l'abonnement
        try:
            subscription = PushSubscription.objects.get(
                arbitre=request.user,
                endpoint=endpoint
            )
            subscription.is_active = False
            subscription.save()
            
            return Response({'detail': 'Désabonnement réussi'}, status=status.HTTP_200_OK)
            
        except PushSubscription.DoesNotExist:
            return Response(
                {'detail': 'Aucun abonnement trouvé pour cet endpoint'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
    except Exception as e:
        print(f"❌ Erreur lors du désabonnement push: {e}")
        return Response(
            {'detail': 'Erreur lors du désabonnement'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def push_subscriptions_status(request):
    """Obtenir le statut des abonnements push de l'utilisateur"""
    try:
        # Vérifier que l'utilisateur est un arbitre
        if not isinstance(request.user, Arbitre):
            return Response(
                {'detail': 'Seuls les arbitres peuvent consulter leurs abonnements push'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Récupérer tous les abonnements de l'arbitre
        subscriptions = PushSubscription.objects.filter(
            arbitre=request.user,
            is_active=True
        ).values('id', 'endpoint', 'created_at', 'last_used')
        
        return Response({
            'subscriptions': list(subscriptions),
            'total_active': len(subscriptions)
        })
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération du statut push: {e}")
        return Response(
            {'detail': 'Erreur lors de la récupération du statut'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def test_push_notification(request):
    """Tester l'envoi d'une notification push (pour les tests)"""
    try:
        # Vérifier que l'utilisateur est un arbitre
        if not isinstance(request.user, Arbitre):
            return Response(
                {'detail': 'Seuls les arbitres peuvent tester les notifications push'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier qu'il y a au moins un abonnement actif
        active_subscriptions = PushSubscription.objects.filter(
            arbitre=request.user,
            is_active=True
        )
        
        if not active_subscriptions.exists():
            return Response(
                {'detail': 'Aucun abonnement push actif trouvé'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Importer le service de notifications
        from notifications.services import push_service
        
        # Envoyer une notification de test
        result = push_service.send_notification_to_arbitres(
            arbitres=[request.user],
            title="🧪 Test de Notification",
            body="Ceci est un test de notification push",
            data={'type': 'test', 'timestamp': timezone.now().isoformat()},
            tag='test'
        )
        
        return Response({
            'detail': 'Notification de test envoyée',
            'result': result
        })
        
    except Exception as e:
        print(f"❌ Erreur lors du test de notification push: {e}")
        return Response(
            {'detail': 'Erreur lors du test de notification'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )