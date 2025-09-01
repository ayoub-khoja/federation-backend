from rest_framework import serializers
from .models import News


class NewsSerializer(serializers.ModelSerializer):
    """Serializer pour les actualités"""
    
    author_name = serializers.SerializerMethodField()
    author_id = serializers.SerializerMethodField()
    author_type = serializers.SerializerMethodField()
    has_media = serializers.ReadOnlyField()
    media_type = serializers.ReadOnlyField()
    
    class Meta:
        model = News
        fields = [
            'id', 'title_fr', 'title_ar', 'content_fr', 'content_ar',
            'image', 'video', 'author_name', 'author_id', 'author_type', 'created_at', 
            'updated_at', 'is_published', 'is_featured', 'order',
            'has_media', 'media_type'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_author_name(self, obj):
        """Récupérer le nom de l'auteur de manière sécurisée"""
        if obj.author:
            if hasattr(obj.author, 'get_full_name'):
                return obj.author.get_full_name()
            elif hasattr(obj.author, 'first_name') and hasattr(obj.author, 'last_name'):
                return f"{obj.author.first_name} {obj.author.last_name}"
            else:
                return str(obj.author)
        return "Auteur inconnu"
    
    def get_author_id(self, obj):
        """Récupérer l'ID de l'auteur"""
        if obj.author:
            return obj.author.id
        return None
    
    def get_author_type(self, obj):
        """Récupérer le type d'auteur"""
        if obj.author:
            return obj.author.__class__.__name__.lower()
        return None
    
    def create(self, validated_data):
        """Créer une nouvelle actualité"""
        # L'auteur sera assigné dans la vue
        return super().create(validated_data)


class NewsCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'actualités"""
    
    class Meta:
        model = News
        fields = [
            'title_fr', 'title_ar', 'content_fr', 'content_ar',
            'image', 'video', 'is_published', 'is_featured', 'order'
        ]
    
    def validate(self, data):
        """Validation des données"""
        # Vérifier qu'au moins un titre est fourni
        if not data.get('title_fr') and not data.get('title_ar'):
            raise serializers.ValidationError("Au moins un titre (français ou arabe) est requis.")
        
        # Vérifier qu'au moins un contenu est fourni
        if not data.get('content_fr') and not data.get('content_ar'):
            raise serializers.ValidationError("Au moins un contenu (français ou arabe) est requis.")
        
        return data


class NewsUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour d'actualités"""
    
    class Meta:
        model = News
        fields = [
            'title_fr', 'title_ar', 'content_fr', 'content_ar',
            'image', 'video', 'is_published', 'is_featured', 'order'
        ]



