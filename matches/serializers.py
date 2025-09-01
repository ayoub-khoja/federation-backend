"""
Serializers pour l'API des matchs
"""
from rest_framework import serializers
from .models import Match, MatchEvent, TypeMatch, Categorie
from .models import Designation

class TypeMatchSerializer(serializers.ModelSerializer):
    """Serializer pour les types de match"""
    
    class Meta:
        model = TypeMatch
        fields = ['id', 'nom', 'code', 'description', 'is_active', 'ordre']

class CategorieSerializer(serializers.ModelSerializer):
    """Serializer pour les catégories"""
    
    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'code', 'age_min', 'age_max', 'description', 'is_active', 'ordre']

class MatchEventSerializer(serializers.ModelSerializer):
    """Serializer pour les événements de match"""
    
    class Meta:
        model = MatchEvent
        fields = [
            'id', 'event_type', 'team', 'player_name', 
            'minute', 'description', 'created_at'
        ]

class MatchSerializer(serializers.ModelSerializer):
    """Serializer pour les matchs"""
    events = MatchEventSerializer(many=True, read_only=True)
    referee_name = serializers.CharField(source='referee.get_full_name', read_only=True)
    type_match_info = TypeMatchSerializer(source='type_match', read_only=True)
    categorie_info = CategorieSerializer(source='categorie', read_only=True)
    score_display = serializers.ReadOnlyField()
    has_score = serializers.ReadOnlyField()
    is_completed = serializers.ReadOnlyField()
    
    class Meta:
        model = Match
        fields = [
            'id', 'type_match', 'categorie', 'type_match_info', 'categorie_info',
            'stadium', 'match_date', 'match_time', 'home_team', 'away_team', 
            'home_score', 'away_score', 'role', 'description', 'match_sheet', 'referee',
            'referee_name', 'status', 'created_at', 'updated_at',
            'match_report', 'incidents', 'events', 'score_display',
            'has_score', 'is_completed'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'referee']
    
    def create(self, validated_data):
        """Créer un nouveau match avec l'arbitre connecté"""
        validated_data['referee'] = self.context['request'].user
        return super().create(validated_data)

class MatchCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de matchs"""
    
    class Meta:
        model = Match
        fields = [
            'type_match', 'categorie', 'stadium', 'match_date',
            'match_time', 'home_team', 'away_team', 'home_score', 'away_score',
            'role', 'description', 'match_sheet'
        ]
    
    def create(self, validated_data):
        """Créer un nouveau match"""
        validated_data['referee'] = self.context['request'].user
        return super().create(validated_data)

class MatchUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour des matchs"""
    
    class Meta:
        model = Match
        fields = [
            'type_match', 'categorie', 'stadium', 'match_date',
            'match_time', 'home_team', 'away_team', 'home_score',
            'away_score', 'role', 'description', 'match_sheet', 'status',
            'match_report', 'incidents'
        ]

class MatchListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des matchs"""
    referee_name = serializers.CharField(source='referee.get_full_name', read_only=True)
    type_match_nom = serializers.SerializerMethodField()
    categorie_nom = serializers.SerializerMethodField()
    score_display = serializers.ReadOnlyField()
    
    def get_type_match_nom(self, obj):
        return obj.type_match.nom if obj.type_match else "Type non défini"
    
    def get_categorie_nom(self, obj):
        return obj.categorie.nom if obj.categorie else "Catégorie non définie"
    
    class Meta:
        model = Match
        fields = [
            'id', 'type_match_nom', 'categorie_nom', 'stadium', 'match_date',
            'match_time', 'home_team', 'away_team', 'score_display', 'role',
            'referee_name', 'status'
        ]

class DesignationSerializer(serializers.ModelSerializer):
    """Serializer pour les désignations d'arbitrage"""
    arbitre_name = serializers.CharField(source='arbitre.get_full_name', read_only=True)
    match_info = serializers.SerializerMethodField()
    type_designation_display = serializers.CharField(source='get_type_designation_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Designation
        fields = [
            'id', 'match', 'arbitre', 'arbitre_name', 'type_designation',
            'type_designation_display', 'status', 'status_display',
            'date_designation', 'date_reponse', 'commentaires',
            'raison_refus', 'notification_envoyee', 'date_notification',
            'match_info'
        ]
        read_only_fields = ['id', 'date_designation', 'date_reponse', 'date_notification']
    
    def get_match_info(self, obj):
        """Informations du match associé"""
        if obj.match:
            return {
                'id': obj.match.id,
                'home_team': obj.match.home_team,
                'away_team': obj.match.away_team,
                'date': obj.match.match_date,
                'time': obj.match.match_time,
                'stadium': obj.match.stadium
            }
        return None

class DesignationCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création de désignations"""
    
    class Meta:
        model = Designation
        fields = [
            'match', 'arbitre', 'type_designation', 'commentaires'
        ]
    
    def validate(self, data):
        """Validation personnalisée"""
        # Vérifier qu'il n'y a pas déjà une désignation pour ce match/arbitre/type
        existing = Designation.objects.filter(
            match=data['match'],
            arbitre=data['arbitre'],
            type_designation=data['type_designation']
        )
        if existing.exists():
            raise serializers.ValidationError(
                "Une désignation existe déjà pour cet arbitre et ce type sur ce match"
            )
        return data

class DesignationUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour des désignations"""
    
    class Meta:
        model = Designation
        fields = [
            'status', 'commentaires', 'raison_refus'
        ]

class DesignationListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la liste des désignations"""
    arbitre_name = serializers.CharField(source='arbitre.get_full_name', read_only=True)
    match_summary = serializers.SerializerMethodField()
    type_designation_display = serializers.CharField(source='get_type_designation_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Designation
        fields = [
            'id', 'arbitre_name', 'type_designation_display', 'status_display',
            'date_designation', 'notification_envoyee', 'match_summary'
        ]
    
    def get_match_summary(self, obj):
        """Résumé du match"""
        if obj.match:
            return f"{obj.match.home_team} vs {obj.match.away_team} - {obj.match.match_date}"
        return "Match non trouvé"





