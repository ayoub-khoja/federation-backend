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
    path('arbitres/register', views.arbitre_register, name='arbitre_register_no_slash'),
    path('arbitres/login/', views.arbitre_login, name='arbitre_login'),
    path('arbitres/login', views.arbitre_login, name='arbitre_login_no_slash'),
    path('arbitres/profile/', views.arbitre_profile, name='arbitre_profile'),
    path('test-auth/', views.test_auth, name='test_auth'),
    path('arbitres/profile/update/', views.arbitre_update_profile, name='arbitre_update_profile'),
    
    # ============================================================================
    # AUTHENTIFICATION COMMISSAIRES
    # ============================================================================
    path('commissaires/register/', views.commissaire_register, name='commissaire_register'),
    path('commissaires/register', views.commissaire_register, name='commissaire_register_no_slash'),
    path('commissaires/login/', views.commissaire_login, name='commissaire_login'),
    path('commissaires/login', views.commissaire_login, name='commissaire_login_no_slash'),
    path('commissaires/profile/', views.commissaire_profile, name='commissaire_profile'),
    path('commissaires/profile/update/', views.commissaire_update_profile, name='commissaire_update_profile'),
    
    # ============================================================================
    # AUTHENTIFICATION ADMINISTRATEURS
    # ============================================================================
    path('admins/register/', views.admin_register, name='admin_register'),
    path('admins/register', views.admin_register, name='admin_register_no_slash'),
    path('admins/login/', views.admin_login, name='admin_login'),
    path('admins/login', views.admin_login, name='admin_login_no_slash'),
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
    # NOTIFICATIONS PUSH (ANCIEN SYSTÈME)
    # ============================================================================
    path('push/subscribe/', views.push_subscribe, name='push_subscribe'),
    path('push/unsubscribe/', views.push_unsubscribe, name='push_unsubscribe'),
    path('push/status/', views.push_subscriptions_status, name='push_subscriptions_status'),
    path('push/test/', views.test_push_notification, name='test_push_notification'),
    
    # ============================================================================
    # FIREBASE CLOUD MESSAGING (FCM) - NOUVEAU SYSTÈME
    # ============================================================================
    path('fcm/subscribe/', views.fcm_subscribe_mobile, name='fcm_subscribe_mobile'),
    path('fcm/subscribe', views.fcm_subscribe_mobile, name='fcm_subscribe_mobile_no_slash'),
    path('fcm/unsubscribe/', views.fcm_unsubscribe_mobile, name='fcm_unsubscribe_mobile'),
    path('fcm/unsubscribe', views.fcm_unsubscribe_mobile, name='fcm_unsubscribe_mobile_no_slash'),
    path('fcm/status/', views.fcm_tokens_status, name='fcm_tokens_status'),
    path('fcm/test/', views.fcm_test_notification, name='fcm_test_notification'),
    path('fcm/stats/', views.fcm_notification_stats, name='fcm_notification_stats'),
    path('fcm/broadcast/', views.fcm_send_broadcast, name='fcm_send_broadcast'),
    
    # ============================================================================
    # NOTIFICATIONS DE DÉSIGNATION D'ARBITRES
    # ============================================================================
    path('arbitres/notify-designation/', views.notify_arbitre_designation, name='notify_arbitre_designation'),
    path('arbitres/notify-multiple/', views.notify_multiple_arbitres, name='notify_multiple_arbitres'),
    path('arbitres/<int:arbitre_id>/notifications/', views.arbitre_notifications_history, name='arbitre_notifications_history'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    
    # ============================================================================
    # EXCUSES D'ARBITRES
    # ============================================================================
    path('arbitres/excuses/', views.create_excuse_arbitre, name='create_excuse_arbitre'),
    path('arbitres/excuses/list/', views.list_excuses_arbitre, name='list_excuses_arbitre'),
    path('arbitres/excuses/<int:excuse_id>/', views.detail_excuse_arbitre, name='detail_excuse_arbitre'),
    path('arbitres/excuses/<int:excuse_id>/update/', views.update_excuse_arbitre, name='update_excuse_arbitre'),
    path('arbitres/excuses/<int:excuse_id>/cancel/', views.cancel_excuse_arbitre, name='cancel_excuse_arbitre'),
]

