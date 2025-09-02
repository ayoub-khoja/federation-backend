"""
URLs pour l'application accounts
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # ============================================================================
    # VÉRIFICATION DE NUMÉRO DE TÉLÉPHONE
    # ============================================================================
    path('verify-phone/', views.verify_phone_number, name='verify_phone_number'),
    path('verify-phone', views.verify_phone_number, name='verify_phone_number_no_slash'),
    
    # ============================================================================
    # AUTHENTIFICATION UNIFIÉE (pour mobile)
    # ============================================================================
    path('auth/login/', views.unified_login, name='unified_login'),
    path('auth/logout/', views.unified_logout, name='unified_logout'),
    
    # ============================================================================
    # AUTHENTIFICATION ARBITRES
    # ============================================================================
    path('arbitres/register/', views.arbitre_register, name='arbitre_register'),
    path('arbitres/login/', views.arbitre_login, name='arbitre_login'),
    path('arbitres/profile/', views.arbitre_profile, name='arbitre_profile'),
    path('test-auth/', views.test_auth, name='test_auth'),
    path('arbitres/profile/update/', views.arbitre_update_profile, name='arbitre_update_profile'),
    
    # ============================================================================
    # AUTHENTIFICATION COMMISSAIRES
    # ============================================================================
    path('commissaires/register/', views.commissaire_register, name='commissaire_register'),
    path('commissaires/login/', views.commissaire_login, name='commissaire_login'),
    path('commissaires/profile/', views.commissaire_profile, name='commissaire_profile'),
    path('commissaires/profile/update/', views.commissaire_update_profile, name='commissaire_update_profile'),
    
    # ============================================================================
    # AUTHENTIFICATION ADMINISTRATEURS
    # ============================================================================
    path('admins/register/', views.admin_register, name='admin_register'),
    path('admins/login/', views.admin_login, name='admin_login'),
    path('admins/profile/', views.admin_profile, name='admin_profile'),
    path('admins/profile/update/', views.admin_update_profile, name='admin_update_profile'),
    
    # ============================================================================
    # FONCTIONNALITÉS COMMUNES
    # ============================================================================
    path('change-password/', views.change_password, name='change_password'),
    
    # ============================================================================
    # GESTION DES LIGUES
    # ============================================================================
    path('ligues/', views.ligues_list, name='ligues_list'),
    path('ligues/create/', views.ligue_create, name='ligue_create'),
    path('ligues/<int:ligue_id>/', views.ligue_detail, name='ligue_detail'),
    path('ligues/<int:ligue_id>/update/', views.ligue_update, name='ligue_update'),
    path('ligues/<int:ligue_id>/delete/', views.ligue_delete, name='ligue_delete'),
    
    # ============================================================================
    # ADMINISTRATION
    # ============================================================================
    path('users/', views.users_list, name='users_list'),
    path('stats/', views.admin_stats, name='admin_stats'),
    
    # ============================================================================
    # TOKENS JWT
    # ============================================================================
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # ============================================================================
    # NOTIFICATIONS PUSH
    # ============================================================================
    path('push/subscribe/', views.push_subscribe, name='push_subscribe'),
    path('push/unsubscribe/', views.push_unsubscribe, name='push_unsubscribe'),
    path('push/status/', views.push_subscriptions_status, name='push_subscriptions_status'),
    path('push/test/', views.test_push_notification, name='test_push_notification'),
]

