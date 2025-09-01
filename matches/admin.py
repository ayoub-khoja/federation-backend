"""
Configuration de l'interface d'administration pour les matchs
"""
from django.contrib import admin
from django.contrib import messages
from .models import Match, MatchEvent, Designation, TypeMatch, Categorie

@admin.register(TypeMatch)
class TypeMatchAdmin(admin.ModelAdmin):
    """Interface d'administration pour les types de match"""
    
    list_display = ['nom', 'code', 'is_active', 'ordre', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['nom', 'code', 'description']
    ordering = ['ordre', 'nom']
    list_editable = ['is_active', 'ordre']

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    """Interface d'administration pour les catégories"""
    
    list_display = ['nom', 'code', 'age_min', 'age_max', 'is_active', 'ordre', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['nom', 'code', 'description']
    ordering = ['ordre', 'nom']
    list_editable = ['is_active', 'ordre']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    """Interface d'administration pour les matchs"""
    
    list_display = [
        'match_date', 'match_time', 'home_team', 'away_team',
        'stadium', 'referee', 'role', 'status', 'score_display'
    ]
    list_filter = [
        'type_match', 'categorie', 'role', 'status', 'match_date'
    ]
    search_fields = [
        'home_team', 'away_team', 'stadium', 'referee__first_name', 
        'referee__last_name', 'referee__phone_number'
    ]
    ordering = ['-match_date', '-match_time']
    date_hierarchy = 'match_date'
    
    fieldsets = (
        ('Informations du match', {
            'fields': ('type_match', 'categorie', 'stadium', 'match_date', 'match_time')
        }),
        ('Équipes', {
            'fields': ('home_team', 'away_team')
        }),
        ('Score', {
            'fields': ('home_score', 'away_score', 'status'),
            'classes': ['collapse']
        }),
        ('Arbitrage', {
            'fields': ('referee', 'role')
        }),
        ('Documents et rapports', {
            'fields': ('description', 'match_sheet', 'match_report', 'incidents'),
            'classes': ['collapse']
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('referee')

@admin.register(MatchEvent)
class MatchEventAdmin(admin.ModelAdmin):
    """Interface d'administration pour les événements de match"""
    
    list_display = [
        'match', 'event_type', 'team', 'player_name', 'minute'
    ]
    list_filter = ['event_type', 'match__match_date']
    search_fields = ['player_name', 'team', 'match__home_team', 'match__away_team']
    ordering = ['match__match_date', 'minute']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('match')

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    """Interface d'administration pour les désignations d'arbitrage"""
    
    list_display = [
        'match', 'arbitre', 'type_designation', 'status', 
        'date_designation', 'notification_envoyee'
    ]
    
    list_filter = [
        'status', 'type_designation', 'date_designation', 
        'notification_envoyee', 'match__match_date'
    ]
    
    search_fields = [
        'arbitre__first_name', 'arbitre__last_name', 'arbitre__phone_number',
        'match__home_team', 'match__away_team', 'match__stadium'
    ]
    
    ordering = ['-date_designation']
    
    date_hierarchy = 'date_designation'
    
    list_editable = ['status']
    
    fieldsets = (
        ('Informations du match', {
            'fields': ('match',)
        }),
        ('Arbitre et type', {
            'fields': ('arbitre', 'type_designation')
        }),
        ('Statut et suivi', {
            'fields': ('status', 'date_designation', 'date_reponse')
        }),
        ('Notifications', {
            'fields': ('notification_envoyee', 'date_notification')
        }),
        ('Commentaires', {
            'fields': ('commentaires', 'raison_refus'),
            'classes': ['collapse']
        }),
    )
    
    readonly_fields = ['date_designation', 'date_reponse', 'date_notification']
    
    actions = [
        'envoyer_notifications_push',
        'confirmer_designations',
        'annuler_designations'
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('arbitre', 'match')
    
    def envoyer_notifications_push(self, request, queryset):
        """Envoyer les notifications push pour les désignations sélectionnées"""
        from notifications.services import push_service
        
        count = 0
        for designation in queryset:
            if not designation.notification_envoyee:
                try:
                    # Préparer les informations du match
                    match_info = {
                        'id': designation.match.id,
                        'home_team': designation.match.home_team,
                        'away_team': designation.match.away_team,
                        'date': designation.match.match_date.isoformat(),
                        'stade': designation.match.stadium,
                        'type_designation': designation.get_type_designation_display()
                    }
                    
                    # Envoyer la notification
                    result = push_service.send_designation_notification(
                        [designation.arbitre], 
                        match_info
                    )
                    
                    if result['success'] > 0:
                        # Marquer comme envoyée
                        designation.marquer_notification_envoyee()
                        count += 1
                    else:
                        messages.warning(
                            request, 
                            f"Échec de l'envoi pour {designation.arbitre.get_full_name()}"
                        )
                        
                except Exception as e:
                    messages.error(
                        request, 
                        f"Erreur pour {designation.arbitre.get_full_name()}: {str(e)}"
                    )
        
        if count > 0:
            messages.success(
                request, 
                f"{count} notification(s) push envoyée(s) avec succès !"
            )
        else:
            messages.warning(request, "Aucune notification envoyée")
    
    envoyer_notifications_push.short_description = "Envoyer les notifications push"
    
    def confirmer_designations(self, request, queryset):
        """Confirmer les désignations sélectionnées"""
        count = queryset.update(status='confirmed')
        messages.success(
            request, 
            f"{count} désignation(s) confirmée(s) avec succès !"
        )
    
    confirmer_designations.short_description = "Confirmer les désignations"
    
    def annuler_designations(self, request, queryset):
        """Annuler les désignations sélectionnées"""
        count = queryset.update(status='cancelled')
        messages.success(
            request, 
            f"{count} désignation(s) annulée(s) avec succès !"
        )
    
    annuler_designations.short_description = "Annuler les désignations"
    
    def save_model(self, request, obj, form, change):
        """Sauvegarder le modèle et envoyer automatiquement la notification"""
        is_new = not change
        super().save_model(request, obj, form, change)
        
        # Si c'est une nouvelle désignation, envoyer automatiquement la notification
        if is_new and not obj.notification_envoyee:
            try:
                from notifications.services import push_service
                
                # Préparer les informations du match
                match_info = {
                    'id': obj.match.id,
                    'home_team': obj.match.home_team,
                    'away_team': obj.match.away_team,
                    'date': obj.match.match_date.isoformat(),
                    'stade': obj.match.stadium,
                    'type_designation': obj.get_type_designation_display()
                }
                
                # Envoyer la notification
                result = push_service.send_designation_notification(
                    [obj.arbitre], 
                    match_info
                )
                
                if result['success'] > 0:
                    # Marquer comme envoyée
                    obj.marquer_notification_envoyee()
                    messages.success(
                        request, 
                        f"Notification push envoyée à {obj.arbitre.get_full_name()}"
                    )
                else:
                    messages.warning(
                        request, 
                        f"Échec de l'envoi de la notification push"
                    )
                    
            except Exception as e:
                messages.error(
                    request, 
                    f"Erreur lors de l'envoi de la notification: {str(e)}"
                )

