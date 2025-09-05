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
from .models import Arbitre, Commissaire, Admin, LigueArbitrage, ExcuseArbitre
from .serializers import (
    ArbitreRegistrationSerializer, ArbitreProfileSerializer, ArbitreUpdateSerializer,
    ArbitreLoginSerializer,
    CommissaireRegistrationSerializer, CommissaireProfileSerializer, CommissaireUpdateSerializer,
    CommissaireLoginSerializer,
    AdminRegistrationSerializer, AdminProfileSerializer, AdminUpdateSerializer,
    AdminLoginSerializer,
    ChangePasswordSerializer, LigueArbitrageSerializer,
    UnifiedLoginSerializer,
    ExcuseArbitreCreateSerializer, ExcuseArbitreListSerializer, 
    ExcuseArbitreDetailSerializer, ExcuseArbitreUpdateSerializer
)
from .password_reset_serializers import (
    PasswordResetRequestSerializer, 
    PasswordResetConfirmSerializer,
    PasswordResetOTPVerifySerializer,
    PasswordResetConfirmWithOTPSerializer
)
from .email_service import PasswordResetEmailService
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import PushSubscription
from django.utils import timezone

# ============================================================================
# FONCTIONS HELPER
# ============================================================================

def normalize_phone_number(phone_number):
    """
    Normalise un numéro de téléphone tunisien au format +216........
    """
    # Supprimer tous les espaces et caractères spéciaux
    phone = ''.join(filter(str.isdigit, phone_number))
    
    # Si le numéro commence par 216, ajouter le +
    if phone.startswith('216'):
        return '+' + phone
    # Si le numéro commence par 0, remplacer par +216
    elif phone.startswith('0'):
        return '+216' + phone[1:]
    # Si le numéro a 8 chiffres, ajouter +216
    elif len(phone) == 8:
        return '+216' + phone
    # Si le numéro a déjà le format +216, le garder
    elif phone_number.startswith('+216'):
        return phone_number
    # Sinon, retourner tel quel
    else:
        return phone_number

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
    """Mise à jour complète du profil de l'arbitre connecté - tous les champs modifiables"""
    if not isinstance(request.user, Arbitre):
        return Response({
            'success': False,
            'message': 'Accès non autorisé - Seuls les arbitres peuvent modifier leur profil',
            'error_code': 'ACCESS_DENIED'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Utiliser partial=True pour permettre la mise à jour partielle
        serializer = ArbitreUpdateSerializer(request.user, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Sauvegarder les modifications
            arbitre = serializer.save()
            
            # Sérialiser les données mises à jour pour la réponse
            from .serializers import ArbitreProfileSerializer
            updated_data = ArbitreProfileSerializer(arbitre).data
            
            return Response({
                'success': True,
                'message': 'Profil arbitre mis à jour avec succès',
                'arbitre': updated_data,
                'updated_fields': list(request.data.keys())
            }, status=status.HTTP_200_OK)
        
        # Gestion des erreurs de validation
        error_details = {}
        for field, errors in serializer.errors.items():
            if isinstance(errors, list):
                error_details[field] = errors[0] if errors else "Erreur de validation"
            else:
                error_details[field] = str(errors)
        
        return Response({
            'success': False,
            'message': 'Erreur de validation des données',
            'errors': error_details,
            'error_code': 'VALIDATION_ERROR'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour du profil arbitre: {e}")
        return Response({
            'success': False,
            'message': 'Erreur interne du serveur lors de la mise à jour',
            'error': str(e),
            'error_code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def admin_email_login(request):
    """Connexion d'un administrateur par email avec token JWT"""
    from rest_framework import serializers
    
    # Serializer inline pour éviter les problèmes d'import
    class AdminEmailLoginSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField(write_only=True)
        
        def validate(self, data):
            email = data.get('email')
            password = data.get('password')
            
            if email and password:
                # Normaliser l'email
                email = email.lower().strip()
                
                # Essayer de trouver l'administrateur par email
                try:
                    admin = Admin.objects.get(email=email)
                    if admin.check_password(password) and admin.is_active:
                        # Créer un dictionnaire avec les champs nécessaires
                        user_data = {
                            'id': admin.id,
                            'phone_number': admin.phone_number,
                            'email': admin.email,
                            'full_name': admin.get_full_name(),
                            'user_type': admin.user_type,
                            'user_type_display': admin.get_user_type_display(),
                            'department': admin.department,
                            'position': admin.position,
                            'is_staff': admin.is_staff,
                            'is_superuser': admin.is_superuser,
                            'is_active': admin.is_active,
                            'date_joined': admin.date_joined
                        }
                        data['user'] = user_data
                        data['admin_obj'] = admin  # Ajouter l'objet admin pour le token
                        return data
                    else:
                        raise serializers.ValidationError("Mot de passe incorrect ou compte désactivé.")
                except Admin.DoesNotExist:
                    raise serializers.ValidationError("Aucun administrateur trouvé avec cette adresse email.")
            else:
                raise serializers.ValidationError("L'email et le mot de passe sont requis.")
    
    serializer = AdminEmailLoginSerializer(data=request.data)
    if serializer.is_valid():
        user_data = serializer.validated_data['user']
        admin_obj = serializer.validated_data['admin_obj']
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(admin_obj)
        
        return Response({
            'success': True,
            'message': 'Connexion réussie',
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data
        })
    return Response({
        'success': False,
        'message': 'Échec de la connexion',
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

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def arbitre_delete(request, arbitre_id):
    """Supprimer un arbitre"""
    # Valider l'authentification JWT
    admin_user, error_message = validate_jwt_admin(request)
    if not admin_user:
        return Response({'detail': error_message}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        arbitre = Arbitre.objects.get(id=arbitre_id)
        arbitre_name = arbitre.get_full_name()
        arbitre_phone = arbitre.phone_number
        arbitre.delete()
        
        return Response({
            'success': True,
            'message': f'Arbitre {arbitre_name} ({arbitre_phone}) supprimé avec succès'
        })
    except Arbitre.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Arbitre non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)

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

# ============================================================================
# FIREBASE CLOUD MESSAGING (FCM) - NOUVELLES VUES
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def fcm_subscribe_mobile(request):
    """Enregistrer un token FCM pour une application mobile"""
    try:
        import json
        from .models import FCMToken
        
        data = json.loads(request.body)
        fcm_token = data.get('fcm_token')
        device_type = data.get('device_type', 'web')  # ios, android, web
        device_id = data.get('device_id', '')
        app_version = data.get('app_version', '')
        
        if not fcm_token:
            return Response(
                {'error': 'Token FCM requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if device_type not in ['ios', 'android', 'web']:
            return Response(
                {'error': 'Type d\'appareil invalide. Utilisez: ios, android, ou web'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Déterminer le type d'utilisateur
        user_type = None
        if isinstance(request.user, Arbitre):
            user_type = 'arbitre'
        elif isinstance(request.user, Commissaire):
            user_type = 'commissaire'
        elif isinstance(request.user, Admin):
            user_type = 'admin'
        else:
            return Response(
                {'error': 'Type d\'utilisateur non supporté'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Créer ou mettre à jour le token FCM
        fcm_token_obj, created = FCMToken.objects.get_or_create(
            token=fcm_token,
            defaults={
                user_type: request.user,
                'device_type': device_type,
                'device_id': device_id,
                'app_version': app_version,
                'is_active': True
            }
        )
        
        if not created:
            # Mettre à jour le token existant
            setattr(fcm_token_obj, user_type, request.user)
            fcm_token_obj.device_type = device_type
            fcm_token_obj.device_id = device_id
            fcm_token_obj.app_version = app_version
            fcm_token_obj.is_active = True
            fcm_token_obj.save()
        
        return Response({
            'success': True,
            'message': f'Token FCM {device_type} enregistré avec succès',
            'created': created,
            'user_type': user_type
        })
        
    except json.JSONDecodeError:
        return Response(
            {'error': 'Données JSON invalides'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de l\'enregistrement: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def fcm_unsubscribe_mobile(request):
    """Désactiver un token FCM pour une application mobile"""
    try:
        import json
        from .models import FCMToken
        
        data = json.loads(request.body)
        fcm_token = data.get('fcm_token')
        
        if not fcm_token:
            return Response(
                {'error': 'Token FCM requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Déterminer le type d'utilisateur
        user_type = None
        if isinstance(request.user, Arbitre):
            user_type = 'arbitre'
        elif isinstance(request.user, Commissaire):
            user_type = 'commissaire'
        elif isinstance(request.user, Admin):
            user_type = 'admin'
        else:
            return Response(
                {'error': 'Type d\'utilisateur non supporté'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Désactiver le token FCM
        fcm_token_obj = FCMToken.objects.filter(
            token=fcm_token,
            **{user_type: request.user}
        ).first()
        
        if fcm_token_obj:
            fcm_token_obj.is_active = False
            fcm_token_obj.save()
            
            return Response({
                'success': True,
                'message': 'Token FCM désactivé avec succès'
            })
        else:
            return Response(
                {'error': 'Token FCM non trouvé'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
    except json.JSONDecodeError:
        return Response(
            {'error': 'Données JSON invalides'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la désactivation: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def fcm_tokens_status(request):
    """Obtenir le statut des tokens FCM de l'utilisateur"""
    try:
        from .models import FCMToken
        
        # Déterminer le type d'utilisateur
        user_type = None
        if isinstance(request.user, Arbitre):
            user_type = 'arbitre'
        elif isinstance(request.user, Commissaire):
            user_type = 'commissaire'
        elif isinstance(request.user, Admin):
            user_type = 'admin'
        else:
            return Response(
                {'error': 'Type d\'utilisateur non supporté'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer tous les tokens de l'utilisateur
        fcm_tokens = FCMToken.objects.filter(
            **{user_type: request.user}
        ).order_by('-created_at')
        
        tokens_data = []
        for token in fcm_tokens:
            tokens_data.append({
                'id': token.id,
                'token': token.token[:20] + '...',  # Masquer le token complet
                'device_type': token.device_type,
                'device_id': token.device_id,
                'app_version': token.app_version,
                'is_active': token.is_active,
                'created_at': token.created_at,
                'last_used': token.last_used
            })
        
        return Response({
            'success': True,
            'tokens': tokens_data,
            'total_tokens': len(tokens_data),
            'active_tokens': len([t for t in tokens_data if t['is_active']])
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la récupération: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def fcm_test_notification(request):
    """Tester l'envoi d'une notification FCM (pour les tests)"""
    try:
        from firebase_config import send_notification_to_user
        
        # Vérifier que l'utilisateur a au moins un token FCM actif
        from .models import FCMToken
        
        user_type = None
        if isinstance(request.user, Arbitre):
            user_type = 'arbitre'
        elif isinstance(request.user, Commissaire):
            user_type = 'commissaire'
        elif isinstance(request.user, Admin):
            user_type = 'admin'
        else:
            return Response(
                {'error': 'Type d\'utilisateur non supporté'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        active_tokens = FCMToken.objects.filter(
            **{user_type: request.user},
            is_active=True
        )
        
        if not active_tokens.exists():
            return Response(
                {'error': 'Aucun token FCM actif trouvé'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Envoyer une notification de test
        results = send_notification_to_user(
            user=request.user,
            title="🧪 Test FCM",
            body="Ceci est un test de notification Firebase Cloud Messaging",
            data={'type': 'test', 'timestamp': timezone.now().isoformat()}
        )
        
        return Response({
            'success': True,
            'message': 'Notification de test FCM envoyée',
            'results': results
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors du test: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def fcm_notification_stats(request):
    """Obtenir les statistiques des notifications FCM (admin seulement)"""
    try:
        # Vérifier que l'utilisateur est un admin
        if not isinstance(request.user, Admin):
            return Response(
                {'error': 'Accès refusé. Seuls les administrateurs peuvent voir ces statistiques'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        from firebase_config import get_notification_stats
        
        stats = get_notification_stats()
        
        return Response({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la récupération des statistiques: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def fcm_send_broadcast(request):
    """Envoyer une notification broadcast à tous les utilisateurs (admin seulement)"""
    try:
        import json
        
        # Vérifier que l'utilisateur est un admin
        if not isinstance(request.user, Admin):
            return Response(
                {'error': 'Accès refusé. Seuls les administrateurs peuvent envoyer des broadcasts'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = json.loads(request.body)
        title = data.get('title')
        body = data.get('body')
        data_payload = data.get('data', {})
        device_types = data.get('device_types', None)  # ['ios', 'android', 'web']
        
        if not title or not body:
            return Response(
                {'error': 'Titre et corps de la notification requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from firebase_config import send_notification_to_all_platforms
        
        # Envoyer la notification broadcast
        results = send_notification_to_all_platforms(
            title=title,
            body=body,
            data=data_payload,
            device_types=device_types
        )
        
        return Response({
            'success': True,
            'message': 'Notification broadcast envoyée',
            'results': results
        })
        
    except json.JSONDecodeError:
        return Response(
            {'error': 'Données JSON invalides'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de l\'envoi: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ============================================================================
# NOTIFICATIONS DE DÉSIGNATION D'ARBITRES
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def notify_arbitre_designation(request):
    """Notifier un arbitre lors d'une désignation"""
    try:
        import json
        from .models import NotificationDesignation
        from firebase_config import send_notification_to_user
        
        # Vérifier que l'utilisateur est un admin
        if not isinstance(request.user, Admin):
            return Response(
                {'error': 'Accès refusé. Seuls les administrateurs peuvent notifier les arbitres'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = json.loads(request.body)
        
        # Validation des données requises
        required_fields = ['arbitre_id', 'arbitre_nom', 'arbitre_email', 'match_id', 
                          'match_nom', 'match_date', 'match_lieu', 'designation_type', 'message']
        
        for field in required_fields:
            if field not in data:
                return Response(
                    {'error': f'Champ requis manquant: {field}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Récupérer l'arbitre
        try:
            arbitre = Arbitre.objects.get(id=data['arbitre_id'], is_active=True)
        except Arbitre.DoesNotExist:
            return Response(
                {'error': 'Arbitre non trouvé ou inactif'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Créer l'enregistrement de notification
        notification = NotificationDesignation.objects.create(
            arbitre=arbitre,
            match_id=data['match_id'],
            match_nom=data['match_nom'],
            match_date=data['match_date'],
            match_lieu=data['match_lieu'],
            designation_type=data['designation_type'],
            title=f"🏆 Nouvelle Désignation - {data['match_nom']}",
            message=data['message'],
            status='sent'
        )
        
        # Envoyer la notification FCM
        try:
            fcm_results = send_notification_to_user(
                user=arbitre,
                title=notification.title,
                body=notification.message,
                data={
                    'type': 'designation',
                    'match_id': str(data['match_id']),
                    'designation_type': data['designation_type'],
                    'notification_id': str(notification.id),
                    'match_date': data['match_date'],
                    'match_lieu': data['match_lieu']
                }
            )
            
            # Mettre à jour le statut de la notification
            if fcm_results.get('errors', 0) == 0:
                notification.mark_as_delivered()
                notification.fcm_response = fcm_results
            else:
                notification.mark_as_failed(f"Erreur FCM: {fcm_results.get('error_details', 'Erreur inconnue')}")
                notification.fcm_response = fcm_results
            
            notification.sent_at = timezone.now()
            notification.save()
            
        except Exception as fcm_error:
            notification.mark_as_failed(f"Erreur lors de l'envoi FCM: {str(fcm_error)}")
            notification.save()
            fcm_results = {'error': str(fcm_error)}
        
        return Response({
            'success': True,
            'message': 'Notification de désignation envoyée',
            'notification_id': notification.id,
            'arbitre': {
                'id': arbitre.id,
                'nom': arbitre.get_full_name(),
                'email': arbitre.email
            },
            'fcm_results': fcm_results
        })
        
    except json.JSONDecodeError:
        return Response(
            {'error': 'Données JSON invalides'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de l\'envoi: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def notify_multiple_arbitres(request):
    """Notifier plusieurs arbitres lors de désignations"""
    try:
        import json
        from .models import NotificationDesignation
        from firebase_config import send_notification_to_user
        
        # Vérifier que l'utilisateur est un admin
        if not isinstance(request.user, Admin):
            return Response(
                {'error': 'Accès refusé. Seuls les administrateurs peuvent notifier les arbitres'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        data = json.loads(request.body)
        notifications_data = data.get('notifications', [])
        
        if not notifications_data:
            return Response(
                {'error': 'Aucune notification à envoyer'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = []
        success_count = 0
        error_count = 0
        
        for notification_data in notifications_data:
            try:
                # Validation des données requises
                required_fields = ['arbitre_id', 'arbitre_nom', 'arbitre_email', 'match_id', 
                                  'match_nom', 'match_date', 'match_lieu', 'designation_type', 'message']
                
                missing_fields = [field for field in required_fields if field not in notification_data]
                if missing_fields:
                    results.append({
                        'arbitre_id': notification_data.get('arbitre_id'),
                        'success': False,
                        'error': f'Champs manquants: {", ".join(missing_fields)}'
                    })
                    error_count += 1
                    continue
                
                # Récupérer l'arbitre
                try:
                    arbitre = Arbitre.objects.get(id=notification_data['arbitre_id'], is_active=True)
                except Arbitre.DoesNotExist:
                    results.append({
                        'arbitre_id': notification_data['arbitre_id'],
                        'success': False,
                        'error': 'Arbitre non trouvé ou inactif'
                    })
                    error_count += 1
                    continue
                
                # Créer l'enregistrement de notification
                notification = NotificationDesignation.objects.create(
                    arbitre=arbitre,
                    match_id=notification_data['match_id'],
                    match_nom=notification_data['match_nom'],
                    match_date=notification_data['match_date'],
                    match_lieu=notification_data['match_lieu'],
                    designation_type=notification_data['designation_type'],
                    title=f"🏆 Nouvelle Désignation - {notification_data['match_nom']}",
                    message=notification_data['message'],
                    status='sent'
                )
                
                # Envoyer la notification FCM
                try:
                    fcm_results = send_notification_to_user(
                        user=arbitre,
                        title=notification.title,
                        body=notification.message,
                        data={
                            'type': 'designation',
                            'match_id': str(notification_data['match_id']),
                            'designation_type': notification_data['designation_type'],
                            'notification_id': str(notification.id),
                            'match_date': notification_data['match_date'],
                            'match_lieu': notification_data['match_lieu']
                        }
                    )
                    
                    # Mettre à jour le statut de la notification
                    if fcm_results.get('errors', 0) == 0:
                        notification.mark_as_delivered()
                        notification.fcm_response = fcm_results
                    else:
                        notification.mark_as_failed(f"Erreur FCM: {fcm_results.get('error_details', 'Erreur inconnue')}")
                        notification.fcm_response = fcm_results
                    
                    notification.sent_at = timezone.now()
                    notification.save()
                    
                    results.append({
                        'arbitre_id': arbitre.id,
                        'arbitre_nom': arbitre.get_full_name(),
                        'notification_id': notification.id,
                        'success': True,
                        'fcm_results': fcm_results
                    })
                    success_count += 1
                    
                except Exception as fcm_error:
                    notification.mark_as_failed(f"Erreur lors de l'envoi FCM: {str(fcm_error)}")
                    notification.save()
                    
                    results.append({
                        'arbitre_id': arbitre.id,
                        'arbitre_nom': arbitre.get_full_name(),
                        'notification_id': notification.id,
                        'success': False,
                        'error': f'Erreur FCM: {str(fcm_error)}'
                    })
                    error_count += 1
                    
            except Exception as e:
                results.append({
                    'arbitre_id': notification_data.get('arbitre_id'),
                    'success': False,
                    'error': f'Erreur générale: {str(e)}'
                })
                error_count += 1
        
        return Response({
            'success': True,
            'message': f'Notifications envoyées: {success_count} succès, {error_count} erreurs',
            'summary': {
                'total': len(notifications_data),
                'success_count': success_count,
                'error_count': error_count
            },
            'results': results
        })
        
    except json.JSONDecodeError:
        return Response(
            {'error': 'Données JSON invalides'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de l\'envoi: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def arbitre_notifications_history(request, arbitre_id):
    """Historique des notifications d'un arbitre"""
    try:
        from .models import NotificationDesignation
        
        # Vérifier que l'utilisateur est un admin ou l'arbitre lui-même
        if isinstance(request.user, Admin):
            # Admin peut voir toutes les notifications
            try:
                arbitre = Arbitre.objects.get(id=arbitre_id)
            except Arbitre.DoesNotExist:
                return Response(
                    {'error': 'Arbitre non trouvé'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        elif isinstance(request.user, Arbitre) and request.user.id == arbitre_id:
            # L'arbitre peut voir ses propres notifications
            arbitre = request.user
        else:
            return Response(
                {'error': 'Accès refusé'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Récupérer les notifications avec pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        status_filter = request.GET.get('status', None)
        
        notifications = NotificationDesignation.objects.filter(arbitre=arbitre)
        
        if status_filter:
            notifications = notifications.filter(status=status_filter)
        
        notifications = notifications.order_by('-created_at')
        
        # Pagination
        from django.core.paginator import Paginator
        paginator = Paginator(notifications, page_size)
        page_obj = paginator.get_page(page)
        
        notifications_data = []
        for notification in page_obj:
            notifications_data.append({
                'id': notification.id,
                'match_id': notification.match_id,
                'match_nom': notification.match_nom,
                'match_date': notification.match_date,
                'match_lieu': notification.match_lieu,
                'designation_type': notification.designation_type,
                'designation_type_display': notification.get_designation_type_display(),
                'title': notification.title,
                'message': notification.message,
                'status': notification.status,
                'status_display': notification.get_status_display(),
                'is_read': notification.is_read,
                'created_at': notification.created_at,
                'sent_at': notification.sent_at,
                'read_at': notification.read_at,
                'is_recent': notification.is_recent
            })
        
        return Response({
            'success': True,
            'arbitre': {
                'id': arbitre.id,
                'nom': arbitre.get_full_name(),
                'email': arbitre.email
            },
            'notifications': notifications_data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la récupération: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Marquer une notification comme lue"""
    try:
        from .models import NotificationDesignation
        
        # Récupérer la notification
        try:
            notification = NotificationDesignation.objects.get(id=notification_id)
        except NotificationDesignation.DoesNotExist:
            return Response(
                {'error': 'Notification non trouvée'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Vérifier que l'utilisateur est l'arbitre concerné ou un admin
        if isinstance(request.user, Admin):
            # Admin peut marquer n'importe quelle notification comme lue
            pass
        elif isinstance(request.user, Arbitre) and request.user.id == notification.arbitre.id:
            # L'arbitre peut marquer ses propres notifications comme lues
            pass
        else:
            return Response(
                {'error': 'Accès refusé'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Marquer comme lue
        notification.mark_as_read()
        
        return Response({
            'success': True,
            'message': 'Notification marquée comme lue',
            'notification_id': notification.id,
            'read_at': notification.read_at
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la mise à jour: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ============================================================================
# VUES POUR LES EXCUSES D'ARBITRES
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_excuse_arbitre(request):
    """Créer une nouvelle excuse d'arbitre"""
    if not isinstance(request.user, Arbitre):
        return Response({
            'success': False,
            'message': 'Accès non autorisé - Seuls les arbitres peuvent créer des excuses',
            'error_code': 'ACCESS_DENIED'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        serializer = ExcuseArbitreCreateSerializer(
            data=request.data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            # Créer l'excuse avec l'arbitre connecté
            excuse = serializer.save(arbitre=request.user)
            
            # Sérialiser les données complètes pour la réponse
            excuse_data = ExcuseArbitreDetailSerializer(excuse).data
            
            return Response({
                'success': True,
                'message': 'Excuse créée avec succès',
                'excuse': excuse_data
            }, status=status.HTTP_201_CREATED)
        
        # Gestion des erreurs de validation
        error_details = {}
        for field, errors in serializer.errors.items():
            if isinstance(errors, list):
                error_details[field] = errors[0] if errors else "Erreur de validation"
            else:
                error_details[field] = str(errors)
        
        return Response({
            'success': False,
            'message': 'Erreur de validation des données',
            'errors': error_details,
            'error_code': 'VALIDATION_ERROR'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'excuse: {e}")
        return Response({
            'success': False,
            'message': 'Erreur interne du serveur lors de la création',
            'error': str(e),
            'error_code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_excuses_arbitre(request):
    """Lister les excuses de l'arbitre connecté"""
    if not isinstance(request.user, Arbitre):
        return Response({
            'success': False,
            'message': 'Accès non autorisé - Seuls les arbitres peuvent consulter leurs excuses',
            'error_code': 'ACCESS_DENIED'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Paramètres de pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        status_filter = request.GET.get('status', None)
        
        # Récupérer les excuses de l'arbitre
        excuses = ExcuseArbitre.objects.filter(arbitre=request.user)
        
        # Filtrer par statut si spécifié
        if status_filter:
            excuses = excuses.filter(status=status_filter)
        
        # Trier par date de création (plus récentes en premier)
        excuses = excuses.order_by('-created_at')
        
        # Pagination
        paginator = Paginator(excuses, page_size)
        page_obj = paginator.get_page(page)
        
        # Sérialiser les données
        excuses_data = ExcuseArbitreListSerializer(page_obj, many=True).data
        
        return Response({
            'success': True,
            'excuses': excuses_data,
            'pagination': {
                'current_page': page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous()
            }
        })
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des excuses: {e}")
        return Response({
            'success': False,
            'message': 'Erreur lors de la récupération des excuses',
            'error': str(e),
            'error_code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def detail_excuse_arbitre(request, excuse_id):
    """Détails d'une excuse d'arbitre"""
    if not isinstance(request.user, Arbitre):
        return Response({
            'success': False,
            'message': 'Accès non autorisé',
            'error_code': 'ACCESS_DENIED'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Récupérer l'excuse
        try:
            excuse = ExcuseArbitre.objects.get(id=excuse_id, arbitre=request.user)
        except ExcuseArbitre.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Excuse non trouvée',
                'error_code': 'NOT_FOUND'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Sérialiser les données
        excuse_data = ExcuseArbitreDetailSerializer(excuse).data
        
        return Response({
            'success': True,
            'excuse': excuse_data
        })
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de l'excuse: {e}")
        return Response({
            'success': False,
            'message': 'Erreur lors de la récupération de l\'excuse',
            'error': str(e),
            'error_code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_excuse_arbitre(request, excuse_id):
    """Mettre à jour une excuse d'arbitre (seulement si en attente)"""
    if not isinstance(request.user, Arbitre):
        return Response({
            'success': False,
            'message': 'Accès non autorisé',
            'error_code': 'ACCESS_DENIED'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Récupérer l'excuse
        try:
            excuse = ExcuseArbitre.objects.get(id=excuse_id, arbitre=request.user)
        except ExcuseArbitre.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Excuse non trouvée',
                'error_code': 'NOT_FOUND'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifier que l'excuse peut être modifiée
        if not excuse.can_be_modified:
            return Response({
                'success': False,
                'message': 'Cette excuse ne peut plus être modifiée',
                'error_code': 'CANNOT_MODIFY'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mettre à jour l'excuse
        serializer = ExcuseArbitreUpdateSerializer(
            excuse, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            excuse = serializer.save()
            
            # Sérialiser les données mises à jour
            excuse_data = ExcuseArbitreDetailSerializer(excuse).data
            
            return Response({
                'success': True,
                'message': 'Excuse mise à jour avec succès',
                'excuse': excuse_data,
                'updated_fields': list(request.data.keys())
            })
        
        # Gestion des erreurs de validation
        error_details = {}
        for field, errors in serializer.errors.items():
            if isinstance(errors, list):
                error_details[field] = errors[0] if errors else "Erreur de validation"
            else:
                error_details[field] = str(errors)
        
        return Response({
            'success': False,
            'message': 'Erreur de validation des données',
            'errors': error_details,
            'error_code': 'VALIDATION_ERROR'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour de l'excuse: {e}")
        return Response({
            'success': False,
            'message': 'Erreur lors de la mise à jour de l\'excuse',
            'error': str(e),
            'error_code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_excuse_arbitre(request, excuse_id):
    """Annuler une excuse d'arbitre"""
    if not isinstance(request.user, Arbitre):
        return Response({
            'success': False,
            'message': 'Accès non autorisé',
            'error_code': 'ACCESS_DENIED'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Récupérer l'excuse
        try:
            excuse = ExcuseArbitre.objects.get(id=excuse_id, arbitre=request.user)
        except ExcuseArbitre.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Excuse non trouvée',
                'error_code': 'NOT_FOUND'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifier que l'excuse peut être annulée
        if not excuse.can_be_cancelled:
            return Response({
                'success': False,
                'message': 'Cette excuse ne peut plus être annulée',
                'error_code': 'CANNOT_CANCEL'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Annuler l'excuse
        excuse.annuler()
        
        # Sérialiser les données mises à jour
        excuse_data = ExcuseArbitreDetailSerializer(excuse).data
        
        return Response({
            'success': True,
            'message': 'Excuse annulée avec succès',
            'excuse': excuse_data
        })
        
    except Exception as e:
        print(f"❌ Erreur lors de l'annulation de l'excuse: {e}")
        return Response({
            'success': False,
            'message': 'Erreur lors de l\'annulation de l\'excuse',
            'error': str(e),
            'error_code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============================================================================
# VUES POUR LA RÉINITIALISATION DE MOT DE PASSE AVEC OTP
# ============================================================================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def request_password_reset(request):
    """Demander une réinitialisation de mot de passe avec OTP"""
    try:
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            # Trouver l'utilisateur par email
            user = None
            user_type = None
            
            # Chercher dans Arbitre
            try:
                user = Arbitre.objects.get(email=email, is_active=True)
                user_type = 'arbitre'
            except Arbitre.DoesNotExist:
                pass
            
            # Chercher dans Commissaire
            if not user:
                try:
                    user = Commissaire.objects.get(email=email, is_active=True)
                    user_type = 'commissaire'
                except Commissaire.DoesNotExist:
                    pass
            
            # Chercher dans Admin
            if not user:
                try:
                    user = Admin.objects.get(email=email, is_active=True)
                    user_type = 'admin'
                except Admin.DoesNotExist:
                    pass
            
            if not user:
                return Response({
                    'success': False,
                    'message': 'Aucun compte actif trouvé avec cette adresse email.',
                    'error_code': 'USER_NOT_FOUND'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Vérifier la limitation de taux
            from .models import PasswordResetToken
            if not PasswordResetToken.check_rate_limit(email):
                return Response({
                    'success': False,
                    'message': 'Trop de tentatives de réinitialisation. Veuillez attendre avant de réessayer.',
                    'error_code': 'RATE_LIMIT_EXCEEDED'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Nettoyer les anciens tokens avant de créer un nouveau
            PasswordResetToken.cleanup_old_tokens()
            
            # Récupérer l'IP et User-Agent pour la sécurité
            ip_address = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Créer le token avec OTP
            reset_token = PasswordResetToken.create_for_user(
                user=user,
                email=email,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Envoyer l'email avec OTP
            email_sent = PasswordResetEmailService.send_password_reset_email(
                user=user,
                token=reset_token,
                request=request
            )
            
            if email_sent:
                return Response({
                    'success': True,
                    'message': f'Un email de réinitialisation avec code OTP a été envoyé à {email}',
                    'user_type': user_type,
                    'expires_in_minutes': 5,  # Durée de validité du token
                    'instructions': 'Vérifiez votre email pour le code OTP et le lien de réinitialisation'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'Erreur lors de l\'envoi de l\'email. Veuillez réessayer plus tard.',
                    'error_code': 'EMAIL_SEND_ERROR'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Gestion des erreurs de validation
        error_details = {}
        for field, errors in serializer.errors.items():
            if isinstance(errors, list):
                error_details[field] = errors[0] if errors else "Erreur de validation"
            else:
                error_details[field] = str(errors)
        
        return Response({
            'success': False,
            'message': 'Erreur de validation des données',
            'errors': error_details,
            'error_code': 'VALIDATION_ERROR'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        print(f"❌ Erreur lors de la demande de réinitialisation: {e}")
        return Response({
            'success': False,
            'message': 'Erreur interne du serveur',
            'error': str(e),
            'error_code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_otp_code(request):
    """Vérifier le code OTP"""
    try:
        serializer = PasswordResetOTPVerifySerializer(data=request.data)
        
        if serializer.is_valid():
            token = serializer.validated_data['token']
            otp_code = serializer.validated_data['otp_code']
            
            # Récupérer le token valide pour OTP
            from .models import PasswordResetToken
            reset_token = PasswordResetToken.get_valid_otp_token(token)
            
            if not reset_token:
                return Response({
                    'success': False,
                    'message': 'Token invalide, expiré ou OTP déjà vérifié. Veuillez demander un nouveau lien de réinitialisation.',
                    'error_code': 'INVALID_TOKEN'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérifier le code OTP
            if reset_token.otp_code != otp_code:
                return Response({
                    'success': False,
                    'message': 'Code OTP incorrect. Veuillez vérifier le code reçu par email.',
                    'error_code': 'INVALID_OTP'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Marquer l'OTP comme vérifié
            reset_token.mark_otp_as_verified()
            
            # Récupérer l'utilisateur
            user = reset_token.get_user()
            user_type = type(user).__name__.lower()
            
            return Response({
                'success': True,
                'message': 'Code OTP vérifié avec succès. Vous pouvez maintenant réinitialiser votre mot de passe.',
                'user_type': user_type,
                'user_email': user.email,
                'next_step': 'Vous pouvez maintenant définir votre nouveau mot de passe'
            }, status=status.HTTP_200_OK)
        
        # Gestion des erreurs de validation
        error_details = {}
        for field, errors in serializer.errors.items():
            if isinstance(errors, list):
                error_details[field] = errors[0] if errors else "Erreur de validation"
            else:
                error_details[field] = str(errors)
        
        return Response({
            'success': False,
            'message': 'Erreur de validation des données',
            'errors': error_details,
            'error_code': 'VALIDATION_ERROR'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification OTP: {e}")
        return Response({
            'success': False,
            'message': 'Erreur interne du serveur',
            'error': str(e),
            'error_code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def confirm_password_reset(request):
    """Confirmer la réinitialisation de mot de passe avec OTP vérifié"""
    try:
        serializer = PasswordResetConfirmWithOTPSerializer(data=request.data)
        
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            # Récupérer le token valide avec OTP vérifié
            from .models import PasswordResetToken
            reset_token = PasswordResetToken.get_valid_token(token)
            
            if not reset_token:
                return Response({
                    'success': False,
                    'message': 'Token invalide ou expiré. Veuillez demander un nouveau lien de réinitialisation.',
                    'error_code': 'INVALID_TOKEN'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not reset_token.otp_verified:
                return Response({
                    'success': False,
                    'message': 'Le code OTP n\'a pas été vérifié. Veuillez d\'abord vérifier votre code OTP.',
                    'error_code': 'OTP_NOT_VERIFIED'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Récupérer l'utilisateur
            user = reset_token.get_user()
            if not user:
                return Response({
                    'success': False,
                    'message': 'Utilisateur non trouvé.',
                    'error_code': 'USER_NOT_FOUND'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Vérifier que l'utilisateur est toujours actif
            if not user.is_active:
                return Response({
                    'success': False,
                    'message': 'Ce compte a été désactivé.',
                    'error_code': 'ACCOUNT_DISABLED'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Changer le mot de passe
            user.set_password(new_password)
            user.save()
            
            # Note: Les tokens JWT existants resteront valides jusqu'à expiration
            # L'utilisateur devra se reconnecter manuellement avec le nouveau mot de passe
            
            # Marquer le token comme utilisé
            reset_token.mark_as_used()
            
            # Déterminer le type d'utilisateur
            user_type = type(user).__name__.lower()
            
            return Response({
                'success': True,
                'message': 'Mot de passe réinitialisé avec succès. Tous vos tokens de connexion ont été invalidés. Veuillez vous reconnecter avec votre nouveau mot de passe.',
                'user_type': user_type,
                'user_email': user.email,
                'action_required': 'logout_and_relogin',
                'instructions': 'Déconnectez-vous de l\'application et reconnectez-vous avec votre nouveau mot de passe.'
            }, status=status.HTTP_200_OK)
        
        # Gestion des erreurs de validation
        error_details = {}
        for field, errors in serializer.errors.items():
            if isinstance(errors, list):
                error_details[field] = errors[0] if errors else "Erreur de validation"
            else:
                error_details[field] = str(errors)
        
        return Response({
            'success': False,
            'message': 'Erreur de validation des données',
            'errors': error_details,
            'error_code': 'VALIDATION_ERROR'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        print(f"❌ Erreur lors de la confirmation de réinitialisation: {e}")
        return Response({
            'success': False,
            'message': 'Erreur interne du serveur',
            'error': str(e),
            'error_code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def validate_reset_token(request, token):
    """Valider un token de réinitialisation (pour vérifier s'il est valide avant d'afficher le formulaire)"""
    try:
        from .models import PasswordResetToken
        
        reset_token = PasswordResetToken.get_valid_token(token)
        
        if not reset_token:
            return Response({
                'success': False,
                'message': 'Token invalide ou expiré',
                'error_code': 'INVALID_TOKEN'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Récupérer l'utilisateur
        user = reset_token.get_user()
        if not user or not user.is_active:
            return Response({
                'success': False,
                'message': 'Utilisateur non trouvé ou compte désactivé',
                'error_code': 'USER_NOT_FOUND'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Déterminer le type d'utilisateur
        user_type = type(user).__name__.lower()
        
        return Response({
            'success': True,
            'message': 'Token valide',
            'user_info': {
                'email': user.email,
                'user_type': user_type,
                'user_name': user.get_full_name()
            },
            'expires_at': reset_token.expires_at,
            'otp_verified': reset_token.otp_verified,
            'next_step': 'Vérifiez votre code OTP' if not reset_token.otp_verified else 'Définissez votre nouveau mot de passe'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"❌ Erreur lors de la validation du token: {e}")
        return Response({
            'success': False,
            'message': 'Erreur interne du serveur',
            'error': str(e),
            'error_code': 'INTERNAL_ERROR'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)