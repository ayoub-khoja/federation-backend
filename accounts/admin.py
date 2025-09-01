"""
Configuration de l'interface d'administration pour les comptes
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import Arbitre, Commissaire, LigueArbitrage, Admin

@admin.register(Admin)
class AdminUserAdmin(UserAdmin):
    """Interface d'administration pour les administrateurs"""
    
    list_display = [
        'phone_number', 'full_name', 'email', 'user_type', 'department', 'position', 'is_active', 'is_staff', 'is_superuser', 'date_joined'
    ]
    list_filter = ['user_type', 'department', 'is_active', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['phone_number', 'first_name', 'last_name', 'email', 'department', 'position']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Informations de connexion', {
            'fields': ('phone_number', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Type d\'utilisateur', {
            'fields': ('user_type', 'department', 'position')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ['collapse']
        }),
        ('Dates importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ['collapse']
        }),
    )
    
    add_fieldsets = (
        ('Créer un nouvel administrateur', {
            'classes': ['wide'],
            'fields': ['phone_number', 'first_name', 'last_name', 'email', 'password1', 'password2', 'user_type', 'department', 'position']
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    
    def full_name(self, obj):
        """Affiche le nom complet dans la liste"""
        return obj.get_full_name()
    full_name.short_description = 'Nom complet'

@admin.register(Arbitre)
class ArbitreAdmin(UserAdmin):
    """Interface d'administration pour les arbitres"""
    
    list_display = [
        'phone_number', 'full_name', 'grade', 'ligue', 'is_active', 'date_joined'
    ]
    list_filter = ['grade', 'ligue', 'is_active', 'date_joined']
    search_fields = ['phone_number', 'first_name', 'last_name', 'email']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Informations de connexion', {
            'fields': ('phone_number', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email', 'birth_date', 'birth_place', 'address', 'cin')
        }),
        ('Informations professionnelles', {
            'fields': ('grade', 'ligue')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ['collapse']
        }),
        ('Dates importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ['collapse']
        }),
    )
    
    add_fieldsets = (
        ('Créer un nouvel arbitre', {
            'classes': ['wide'],
            'fields': ['phone_number', 'first_name', 'last_name', 'password1', 'password2', 'grade', 'ligue', 'birth_date', 'birth_place', 'address', 'cin']
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    
    def full_name(self, obj):
        """Affiche le nom complet dans la liste"""
        return obj.get_full_name()
    full_name.short_description = 'Nom complet'
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        return super().get_queryset(request).select_related('ligue')

@admin.register(Commissaire)
class CommissaireAdmin(UserAdmin):
    """Interface d'administration pour les commissaires"""
    
    list_display = [
        'phone_number', 'full_name', 'specialite', 'grade', 'ligue', 'is_active', 'date_joined'
    ]
    list_filter = ['specialite', 'grade', 'ligue', 'is_active', 'date_joined']
    search_fields = ['phone_number', 'first_name', 'last_name', 'email']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('Informations de connexion', {
            'fields': ('phone_number', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email', 'birth_date', 'birth_place', 'address', 'cin')
        }),
        ('Informations professionnelles', {
            'fields': ('specialite', 'grade', 'ligue')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ['collapse']
        }),
        ('Dates importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ['collapse']
        }),
    )
    
    add_fieldsets = (
        ('Créer un nouveau commissaire', {
            'classes': ['wide'],
            'fields': ['phone_number', 'first_name', 'last_name', 'password1', 'password2', 'specialite', 'grade', 'ligue', 'birth_date', 'birth_place', 'address', 'cin']
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    
    def full_name(self, obj):
        """Affiche le nom complet dans la liste"""
        return obj.get_full_name()
    full_name.short_description = 'Nom complet'
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        return super().get_queryset(request).select_related('ligue')

@admin.register(LigueArbitrage)
class LigueArbitrageAdmin(admin.ModelAdmin):
    """Interface d'administration pour les ligues d'arbitrage"""
    
    list_display = ['nom', 'ordre', 'is_active', 'date_creation']
    list_filter = ['is_active', 'date_creation']
    search_fields = ['nom', 'description']
    ordering = ['ordre', 'nom']
    list_editable = ['is_active', 'ordre']
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('nom', 'description')
        }),
        ('Configuration', {
            'fields': ('ordre', 'is_active')
        }),
    )
    
    def get_queryset(self, request):
        """Optimise les requêtes"""
        return super().get_queryset(request)

# Configuration du site d'administration
admin.site.site_header = "Direction Nationale de l'Arbitrage"
admin.site.site_title = "Administration DNA"
admin.site.index_title = "Gestion des Comptes"

