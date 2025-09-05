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
    
    # ===== MATCHS PAR TYPE =====
    path('ligue1/', views.Ligue1MatchesView.as_view(), name='ligue1_matches'),
    path('ligue2/', views.Ligue2MatchesView.as_view(), name='ligue2_matches'),
    path('c1/', views.C1MatchesView.as_view(), name='c1_matches'),
    path('c2/', views.C2MatchesView.as_view(), name='c2_matches'),
    path('jeunes/', views.JeunesMatchesView.as_view(), name='jeunes_matches'),
    path('coupe-tunisie/', views.CoupeTunisieMatchesView.as_view(), name='coupe_tunisie_matches'),
    
    # ===== API GÉNÉRIQUE PAR TYPE =====
    path('type/<str:type_code>/', views.matches_by_type, name='matches_by_type'),
    
    # ===== EXCUSES D'ARBITRES =====
    path('excuses/', views.ExcuseArbitreListCreateView.as_view(), name='excuse_list_create'),
    path('excuses/<int:pk>/', views.ExcuseArbitreDetailView.as_view(), name='excuse_detail'),
    path('excuses/statistics/', views.excuses_arbitre_statistics, name='excuse_statistics'),
    
    # ===== EXCUSES PAR DATE =====
    path('excuses/passees/', views.excuses_passees_par_date, name='excuses_passees_par_date'),
    path('excuses/en-cours/', views.excuses_en_cours_par_date, name='excuses_en_cours_par_date'),
    path('excuses/a-venir/', views.excuses_a_venir_par_date, name='excuses_a_venir_par_date'),
    
    # ===== TARIFICATION DES MATCHS =====
    path('tarification/', views.TarificationMatchListView.as_view(), name='tarification_list'),
    path('tarification/<int:pk>/', views.TarificationMatchDetailView.as_view(), name='tarification_detail'),
    path('tarification/create/', views.TarificationMatchCreateView.as_view(), name='tarification_create'),
    path('tarification/<int:pk>/update/', views.TarificationMatchUpdateView.as_view(), name='tarification_update'),
    
    # ===== TARIFICATION PAR FILTRES =====
    path('tarification/competition/<str:competition>/', views.tarification_by_competition, name='tarification_by_competition'),
    path('tarification/competition/<str:competition>/type/<str:type_match>/', views.tarification_by_type_match, name='tarification_by_type_match'),
    path('tarification/competition/<str:competition>/type/<str:type_match>/role/<str:role>/', views.tarification_by_role, name='tarification_by_role'),
]





