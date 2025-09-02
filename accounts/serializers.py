"""
Serializers pour l'API des utilisateurs du système d'arbitrage
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Arbitre, Commissaire, Admin, LigueArbitrage

# ============================================================================
# SÉRIALISEURS POUR L'AUTHENTIFICATION UNIFIÉE
# ============================================================================

class UnifiedLoginSerializer(serializers.Serializer):
    """Serializer pour l'authentification unifiée (mobile)"""
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Validation de la connexion unifiée"""
        phone_number = data.get('phone_number')
        password = data.get('password')
        
        if not phone_number or not password:
            raise serializers.ValidationError("Le numéro de téléphone et le mot de passe sont requis.")
        
        # Nettoyer le numéro de téléphone
        cleaned_phone = self._clean_phone_number(phone_number)
        
        # Essayer de trouver l'utilisateur (arbitre, commissaire, ou admin)
        user = self._find_user_by_phone(cleaned_phone)
        
        if user and user.check_password(password) and user.is_active:
            data['user'] = user
            data['user_type'] = self._get_user_type(user)
            return data
        else:
            raise serializers.ValidationError("Numéro de téléphone ou mot de passe incorrect.")
    
    def _clean_phone_number(self, phone_number):
        """Nettoie et formate le numéro de téléphone au format +216........"""
        # Supprimer les espaces et caractères spéciaux
        cleaned = ''.join(filter(str.isdigit, phone_number))
        
        # Ajouter le préfixe +216 si nécessaire
        if len(cleaned) == 8:
            return '+216' + cleaned
        elif len(cleaned) == 10 and cleaned.startswith('216'):
            return '+' + cleaned
        elif len(cleaned) == 11 and cleaned.startswith('216'):
            return '+' + cleaned
        elif len(cleaned) == 12 and cleaned.startswith('216'):
            return '+' + cleaned
        elif phone_number.startswith('+216'):
            return phone_number
        else:
            return phone_number  # Retourner tel quel si format non reconnu
    
    def _find_user_by_phone(self, phone_number):
        """Trouve l'utilisateur par numéro de téléphone"""
        # Essayer de trouver un arbitre
        try:
            return Arbitre.objects.get(phone_number=phone_number)
        except Arbitre.DoesNotExist:
            pass
        
        # Essayer de trouver un commissaire
        try:
            return Commissaire.objects.get(phone_number=phone_number)
        except Commissaire.DoesNotExist:
            pass
        
        # Essayer de trouver un admin
        try:
            return Admin.objects.get(phone_number=phone_number)
        except Admin.DoesNotExist:
            pass
        
        return None
    
    def _get_user_type(self, user):
        """Détermine le type d'utilisateur"""
        if isinstance(user, Arbitre):
            return 'arbitre'
        elif isinstance(user, Commissaire):
            return 'commissaire'
        elif isinstance(user, Admin):
            return 'admin'
        else:
            return 'unknown'

# ============================================================================
# SÉRIALISEURS POUR LES ARBITRES
# ============================================================================

class ArbitreRegistrationSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription d'un arbitre"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    ligue_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Arbitre
        fields = [
            'phone_number', 'email', 'first_name', 'last_name',
            'address', 'profile_photo', 'ligue_id', 'grade', 
            'birth_date', 'birth_place', 'role', 'password', 'password_confirm'
        ]
        extra_kwargs = {
            'email': {'required': False},
            'address': {'required': False},
            'birth_place': {'required': False},
            'profile_photo': {'required': False},
            'birth_date': {'required': False},
        }
    
    def validate(self, data):
        """Validation des données"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        
        # Valider que la ligue existe
        ligue_id = data.get('ligue_id')
        if ligue_id:
            try:
                ligue = LigueArbitrage.objects.get(id=ligue_id, is_active=True)
                data['ligue'] = ligue
            except LigueArbitrage.DoesNotExist:
                raise serializers.ValidationError(f"La ligue avec l'ID '{ligue_id}' n'existe pas ou n'est pas active.")
        
        # Valider le grade
        grade = data.get('grade')
        if grade:
            valid_grades = ['candidat', '3eme_serie', '2eme_serie', '1ere_serie', 'federale']
            if grade not in valid_grades:
                raise serializers.ValidationError({
                    'grade': f"Le grade '{grade}' n'est pas valide. Grades acceptés: {', '.join(valid_grades)}"
                })
        
        # Valider le rôle
        role = data.get('role')
        if role:
            valid_roles = ['arbitre', 'assistant']
            if role not in valid_roles:
                raise serializers.ValidationError({
                    'role': f"Le rôle '{role}' n'est pas valide. Rôles acceptés: {', '.join(valid_roles)}"
                })
        
        # Valider l'unicité du numéro de téléphone
        phone_number = data.get('phone_number')
        if phone_number:
            # Nettoyer le numéro de téléphone
            cleaned_phone = self._clean_phone_number(phone_number)
            data['phone_number'] = cleaned_phone
            
            # Vérifier si le numéro existe déjà
            if Arbitre.objects.filter(phone_number=cleaned_phone).exists():
                raise serializers.ValidationError({
                    'phone_number': f"Le numéro de téléphone {cleaned_phone} est déjà utilisé par un autre arbitre. Veuillez utiliser un numéro différent."
                })
        
        return data
    
    def _clean_phone_number(self, phone_number):
        """Nettoie et formate le numéro de téléphone au format +216........"""
        # Supprimer les espaces et caractères spéciaux
        cleaned = ''.join(filter(str.isdigit, phone_number))
        
        # Ajouter le préfixe +216 si nécessaire
        if len(cleaned) == 8:
            return '+216' + cleaned
        elif len(cleaned) == 10 and cleaned.startswith('216'):
            return '+' + cleaned
        elif len(cleaned) == 11 and cleaned.startswith('216'):
            return '+' + cleaned
        elif len(cleaned) == 12 and cleaned.startswith('216'):
            return '+' + cleaned
        elif phone_number.startswith('+216'):
            return phone_number
        else:
            return phone_number  # Retourner tel quel si format non reconnu
    
    def create(self, validated_data):
        """Créer un nouvel arbitre"""
        validated_data.pop('password_confirm')
        ligue_id = validated_data.pop('ligue_id')
        password = validated_data.pop('password')
        
        # Normaliser le numéro de téléphone
        phone_number = validated_data.get('phone_number')
        if phone_number:
            validated_data['phone_number'] = self._normalize_phone_number(phone_number)
        
        # Récupérer la ligue
        try:
            from .models import LigueArbitrage
            ligue = LigueArbitrage.objects.get(id=ligue_id)
            validated_data['ligue'] = ligue
        except LigueArbitrage.DoesNotExist:
            raise serializers.ValidationError("Ligue non trouvée")
        
        arbitre = Arbitre.objects.create_user(password=password, **validated_data)
        return arbitre
    
    def _normalize_phone_number(self, phone_number):
        """Normalise un numéro de téléphone tunisien au format +216........"""
        # Supprimer tous les espaces et caractères spéciaux
        phone = ''.join(filter(str.isdigit, phone_number))
        
        # Si le numéro commence par 216, ajouter le +
        if phone.startswith('216'):
            return '+' + phone
        # Si le numéro commence par 0, remplacer par +216
        elif phone.startswith('0'):
            return '+216' + phone[1:]
        # Si le numéro a 8 chiffres, ajouter +216
        elif len(phone) == 8:
            return '+216' + phone
        # Si le numéro a déjà le format +216, le garder
        elif phone_number.startswith('+216'):
            return phone_number
        # Sinon, retourner tel quel
        else:
            return phone_number

class ArbitreLoginSerializer(serializers.Serializer):
    """Serializer pour la connexion des arbitres"""
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Validation de la connexion"""
        phone_number = data.get('phone_number')
        password = data.get('password')
        
        if phone_number and password:
            # Nettoyer le numéro de téléphone
            if not phone_number.startswith('+216'):
                if phone_number.startswith('216'):
                    phone_number = '+' + phone_number
                elif len(phone_number) == 8:
                    phone_number = '+216' + phone_number
            
            # Essayer de trouver l'arbitre
            try:
                arbitre = Arbitre.objects.get(phone_number=phone_number)
                if arbitre.check_password(password) and arbitre.is_active:
                    data['user'] = arbitre
                    return data
                else:
                    raise serializers.ValidationError("Mot de passe incorrect ou compte désactivé.")
            except Arbitre.DoesNotExist:
                raise serializers.ValidationError("Aucun arbitre trouvé avec ce numéro de téléphone.")
        else:
            raise serializers.ValidationError("Le numéro de téléphone et le mot de passe sont requis.")

class ArbitreProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil de l'arbitre"""
    full_name = serializers.ReadOnlyField()
    ligue_nom = serializers.CharField(source='ligue.nom', read_only=True)
    
    class Meta:
        model = Arbitre
        fields = [
            'id', 'phone_number', 'email', 'first_name', 'last_name',
            'full_name', 'role', 'grade', 'ligue', 'ligue_nom',
            'address', 'birth_date', 'birth_place', 'cin',
            'profile_photo', 'date_joined', 'is_active', 'is_staff', 'is_superuser'
        ]
        read_only_fields = ['id', 'phone_number', 'date_joined', 'is_active', 'is_staff', 'is_superuser']

class ArbitreUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour du profil arbitre"""
    
    class Meta:
        model = Arbitre
        fields = [
            'email', 'first_name', 'last_name', 'address', 
            'birth_date', 'birth_place', 'cin', 'profile_photo'
        ]

# ============================================================================
# SÉRIALISEURS POUR LES COMMISSAIRES
# ============================================================================

class CommissaireRegistrationSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription d'un commissaire"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    ligue_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Commissaire
        fields = [
            'phone_number', 'email', 'first_name', 'last_name',
            'specialite', 'grade', 'address', 'birth_date', 'birth_place', 'cin',
            'password', 'password_confirm', 'ligue_id'
        ]
        extra_kwargs = {
            'email': {'required': False},
            'address': {'required': False},
            'birth_place': {'required': False},
            'cin': {'required': False},
        }
    
    def validate(self, data):
        """Validation des données"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        
        # Valider que la ligue existe
        ligue_id = data.get('ligue_id')
        if ligue_id:
            try:
                ligue = LigueArbitrage.objects.get(id=ligue_id, is_active=True)
                data['ligue'] = ligue
            except LigueArbitrage.DoesNotExist:
                raise serializers.ValidationError(f"La ligue avec l'ID '{ligue_id}' n'existe pas ou n'est pas active.")
        
        return data
    
    def create(self, validated_data):
        """Créer un nouveau commissaire"""
        validated_data.pop('password_confirm')
        ligue_id = validated_data.pop('ligue_id')
        password = validated_data.pop('password')
        
        # Normaliser le numéro de téléphone
        phone_number = validated_data.get('phone_number')
        if phone_number:
            validated_data['phone_number'] = self._normalize_phone_number(phone_number)
        
        # Récupérer la ligue
        try:
            from .models import LigueArbitrage
            ligue = LigueArbitrage.objects.get(id=ligue_id)
            validated_data['ligue'] = ligue
        except LigueArbitrage.DoesNotExist:
            raise serializers.ValidationError("Ligue non trouvée")
        
        commissaire = Commissaire.objects.create_user(password=password, **validated_data)
        return commissaire
    
    def _normalize_phone_number(self, phone_number):
        """Normalise un numéro de téléphone tunisien au format +216........"""
        # Supprimer tous les espaces et caractères spéciaux
        phone = ''.join(filter(str.isdigit, phone_number))
        
        # Si le numéro commence par 216, ajouter le +
        if phone.startswith('216'):
            return '+' + phone
        # Si le numéro commence par 0, remplacer par +216
        elif phone.startswith('0'):
            return '+216' + phone[1:]
        # Si le numéro a 8 chiffres, ajouter +216
        elif len(phone) == 8:
            return '+216' + phone
        # Si le numéro a déjà le format +216, le garder
        elif phone_number.startswith('+216'):
            return phone_number
        # Sinon, retourner tel quel
        else:
            return phone_number

class CommissaireLoginSerializer(serializers.Serializer):
    """Serializer pour la connexion des commissaires"""
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Validation de la connexion"""
        phone_number = data.get('phone_number')
        password = data.get('password')
        
        if phone_number and password:
            # Nettoyer le numéro de téléphone
            if not phone_number.startswith('+216'):
                if phone_number.startswith('216'):
                    phone_number = '+' + phone_number
                elif len(phone_number) == 8:
                    phone_number = '+216' + phone_number
            
            # Essayer de trouver le commissaire
            try:
                commissaire = Commissaire.objects.get(phone_number=phone_number)
                if commissaire.check_password(password) and commissaire.is_active:
                    data['user'] = commissaire
                    return data
                else:
                    raise serializers.ValidationError("Mot de passe incorrect ou compte désactivé.")
            except Commissaire.DoesNotExist:
                raise serializers.ValidationError("Aucun commissaire trouvé avec ce numéro de téléphone.")
        else:
            raise serializers.ValidationError("Le numéro de téléphone et le mot de passe sont requis.")

class CommissaireProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil du commissaire"""
    full_name = serializers.ReadOnlyField()
    ligue_nom = serializers.CharField(source='ligue.nom', read_only=True)
    
    class Meta:
        model = Commissaire
        fields = [
            'id', 'phone_number', 'email', 'first_name', 'last_name',
            'full_name', 'specialite', 'grade', 'ligue', 'ligue_nom',
            'address', 'birth_date', 'birth_place', 'cin',
            'date_joined', 'is_active', 'is_staff', 'is_superuser'
        ]
        read_only_fields = ['id', 'phone_number', 'date_joined', 'is_active', 'is_staff', 'is_superuser']

class CommissaireUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour du profil commissaire"""
    
    class Meta:
        model = Commissaire
        fields = [
            'email', 'first_name', 'last_name', 'address', 
            'birth_date', 'birth_place', 'cin'
        ]

# ============================================================================
# SÉRIALISEURS POUR LES ADMINISTRATEURS
# ============================================================================

class AdminRegistrationSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription d'un administrateur"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Admin
        fields = [
            'phone_number', 'email', 'first_name', 'last_name',
            'user_type', 'department', 'position',
            'password', 'password_confirm'
        ]
        extra_kwargs = {
            'department': {'required': False},
            'position': {'required': False},
        }
    
    def validate(self, data):
        """Validation des données"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data
    
    def create(self, validated_data):
        """Créer un nouvel administrateur"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Normaliser le numéro de téléphone
        phone_number = validated_data.get('phone_number')
        if phone_number:
            validated_data['phone_number'] = self._normalize_phone_number(phone_number)
        
        admin = Admin.objects.create_user(password=password, **validated_data)
        return admin
    
    def _normalize_phone_number(self, phone_number):
        """Normalise un numéro de téléphone tunisien au format +216........"""
        # Supprimer tous les espaces et caractères spéciaux
        phone = ''.join(filter(str.isdigit, phone_number))
        
        # Si le numéro commence par 216, ajouter le +
        if phone.startswith('216'):
            return '+' + phone
        # Si le numéro commence par 0, remplacer par +216
        elif phone.startswith('0'):
            return '+216' + phone[1:]
        # Si le numéro a 8 chiffres, ajouter +216
        elif len(phone) == 8:
            return '+216' + phone
        # Si le numéro a déjà le format +216, le garder
        elif phone_number.startswith('+216'):
            return phone_number
        # Sinon, retourner tel quel
        else:
            return phone_number

class AdminLoginSerializer(serializers.Serializer):
    """Serializer pour la connexion des administrateurs"""
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Validation de la connexion"""
        phone_number = data.get('phone_number')
        password = data.get('password')
        
        if phone_number and password:
            # Nettoyer le numéro de téléphone
            if not phone_number.startswith('+216'):
                if phone_number.startswith('216'):
                    phone_number = '+' + phone_number
                elif len(phone_number) == 8:
                    phone_number = '+216' + phone_number
            
            # Essayer de trouver l'administrateur
            try:
                admin = Admin.objects.get(phone_number=phone_number)
                if admin.check_password(password) and admin.is_active:
                    # Créer un dictionnaire avec les champs nécessaires
                    user_data = {
                        'id': admin.id,
                        'phone_number': admin.phone_number,
                        'full_name': admin.get_full_name(),
                        'user_type': admin.user_type,
                        'user_type_display': admin.get_user_type_display(),
                        'department': admin.department,
                        'position': admin.position,
                        'is_staff': admin.is_staff,
                        'is_superuser': admin.is_superuser,
                        'is_active': admin.is_active,
                        'date_joined': admin.date_joined
                    }
                    data['user'] = user_data
                    return data
                else:
                    raise serializers.ValidationError("Mot de passe incorrect ou compte désactivé.")
            except Admin.DoesNotExist:
                raise serializers.ValidationError("Aucun administrateur trouvé avec ce numéro de téléphone.")
        else:
            raise serializers.ValidationError("Le numéro de téléphone et le mot de passe sont requis.")

class AdminProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil de l'administrateur"""
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Admin
        fields = [
            'id', 'phone_number', 'email', 'first_name', 'last_name',
            'full_name', 'user_type', 'department', 'position',
            'date_joined', 'is_active', 'is_staff', 'is_superuser'
        ]
        read_only_fields = ['id', 'phone_number', 'date_joined', 'is_active', 'is_staff', 'is_superuser']

class AdminUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour du profil administrateur"""
    
    class Meta:
        model = Admin
        fields = [
            'email', 'first_name', 'last_name', 'department', 'position'
        ]

# ============================================================================
# SÉRIALISEURS COMMUNS
# ============================================================================

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour changer le mot de passe"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    
    def validate_old_password(self, value):
        """Valider l'ancien mot de passe"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("L'ancien mot de passe est incorrect.")
        return value

class LigueArbitrageSerializer(serializers.ModelSerializer):
    """Serializer pour les ligues d'arbitrage"""
    
    class Meta:
        model = LigueArbitrage
        fields = ['id', 'nom', 'description', 'is_active', 'date_creation', 'ordre']

