"""
URLs pour l'application news
"""
from django.urls import path
from . import views

urlpatterns = [
    # APIs publiques pour les actualités
    path('', views.news_list, name='news_list'),
    path('<int:news_id>/', views.news_detail, name='news_detail'),
    
    # APIs d'administration
    path('admin/list/', views.admin_news_list, name='admin_news_list'),
    path('admin/create/', views.create_news, name='create_news'),
    path('admin/<int:news_id>/update/', views.update_news, name='update_news'),
    path('admin/<int:news_id>/delete/', views.delete_news, name='delete_news'),
    path('admin/<int:news_id>/toggle-featured/', views.toggle_featured, name='toggle_featured'),
]



































