from django.contrib import admin
from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title_fr', 'title_ar', 'get_author_name', 'created_at', 'is_published', 'is_featured']
    list_filter = ['is_published', 'is_featured', 'created_at', 'content_type']
    search_fields = ['title_fr', 'title_ar', 'content_fr', 'content_ar']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
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
            'fields': ('content_type', 'object_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_author_name(self, obj):
        """Afficher le nom de l'auteur de manière sécurisée"""
        if obj.author:
            if hasattr(obj.author, 'get_full_name'):
                return obj.author.get_full_name()
            elif hasattr(obj.author, 'first_name') and hasattr(obj.author, 'last_name'):
                return f"{obj.author.first_name} {obj.author.last_name}"
            else:
                return str(obj.author)
        return "Auteur inconnu"
    get_author_name.short_description = "Auteur"
    get_author_name.admin_order_field = 'object_id'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Création
            from django.contrib.contenttypes.models import ContentType
            obj.content_type = ContentType.objects.get_for_model(request.user)
            obj.object_id = request.user.id
        super().save_model(request, obj, form, change)