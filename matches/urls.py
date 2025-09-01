"""
URLs pour l'application matches
"""
from django.urls import path
from . import views

urlpatterns = [
    # CRUD des matchs
    path('', views.MatchListCreateView.as_view(), name='match_list_create'),
    path('<int:pk>/', views.MatchDetailView.as_view(), name='match_detail'),
    
    # Actions spécifiques
    path('<int:match_id>/complete/', views.complete_match, name='complete_match'),
    
    # Vues de consultation
    path('statistics/', views.match_statistics, name='match_statistics'),
    path('recent/', views.recent_matches, name='recent_matches'),
    path('upcoming/', views.upcoming_matches, name='upcoming_matches'),
    
    # ===== DÉSIGNATIONS =====
    path('designations/', views.DesignationListCreateView.as_view(), name='designation_list_create'),
    path('designations/<int:pk>/', views.DesignationDetailView.as_view(), name='designation_detail'),
    path('designations/<int:designation_id>/accept/', views.accept_designation, name='accept_designation'),
    path('designations/<int:designation_id>/decline/', views.decline_designation, name='decline_designation'),
    path('designations/statistics/', views.designation_statistics, name='designation_statistics'),
    path('designations/my/', views.my_designations, name='my_designations'),
    
    # ===== TYPES DE MATCH ET CATÉGORIES =====
    path('types/', views.match_types, name='match_types'),
    path('categories/', views.categories, name='categories'),
    path('roles/', views.match_roles, name='match_roles'),
]





