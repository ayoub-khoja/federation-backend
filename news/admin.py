from django.contrib import admin
from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title_fr', 'title_ar', 'author', 'created_at', 'is_published', 'is_featured']
    list_filter = ['is_published', 'is_featured', 'created_at', 'author']
    search_fields = ['title_fr', 'title_ar', 'content_fr', 'content_ar']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Contenu en Français', {
            'fields': ('title_fr', 'content_fr')
        }),
        ('Contenu en Arabe', {
            'fields': ('title_ar', 'content_ar')
        }),
        ('Médias', {
            'fields': ('image', 'video')
        }),
        ('Options', {
            'fields': ('is_published', 'is_featured', 'order')
        }),
        ('Métadonnées', {
            'fields': ('author',),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Création
            obj.author = request.user
        super().save_model(request, obj, form, change)