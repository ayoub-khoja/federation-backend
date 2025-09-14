"""
Modèles pour la gestion des utilisateurs du système d'arbitrage
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model

class LigueArbitrage(models.Model):
    """Modèle pour les ligues d'arbitrage"""
    
    nom = models.CharField(max_length=100, verbose_name="Nom de la ligue")
    description = models.TextField(blank=True, verbose_name="Description")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    is_active = models.BooleanField(default=True, verbose_name="Ligue active")
    ordre = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    
    class Meta:
        verbose_name = "Ligue d'arbitrage"
        verbose_name_plural = "Ligues d'arbitrage"
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return f"{self.nom}"

class GradeArbitrage(models.Model):
    """Modèle pour les grades d'arbitrage"""
    
    nom = models.CharField(max_length=100, verbose_name="Nom du grade")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    description = models.TextField(blank=True, verbose_name="Description")
    niveau = models.IntegerField(default=1, verbose_name="Niveau du grade")
    ordre = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    is_active = models.BooleanField(default=True, verbose_name="Grade actif")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    class Meta:
        verbose_name = "Grade d'arbitrage"
        verbose_name_plural = "Grades d'arbitrage"
        ordering = ['ordre', 'niveau', 'nom']
    
    def __str__(self):
        return f"{self.nom}"

# ============================================================================
# MODÈLE ARBITRE
# ============================================================================

class ArbitreManager(BaseUserManager):
    """Gestionnaire personnalisé pour le modèle Arbitre"""
    
    def create_user(self, phone_number, first_name, last_name, password=None, **extra_fields):
        """Créer un utilisateur arbitre normal"""
        if not phone_number:
            raise ValueError('Le numéro de téléphone est obligatoire')
        if not first_name:
            raise ValueError('Le prénom est obligatoire')
        if not last_name:
            raise ValueError('Le nom est obligatoire')
        
        user = self.model(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, first_name, last_name, password=None, **extra_fields):
        """Créer un super utilisateur arbitre"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le super utilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le super utilisateur doit avoir is_superuser=True.')
        
        return self.create_user(phone_number, first_name, last_name, password, **extra_fields)

class Arbitre(AbstractBaseUser, PermissionsMixin):
    """Modèle pour les arbitres (mobile uniquement)"""
    
    # Validation du numéro de téléphone tunisien
    phone_regex = RegexValidator(
        regex=r'^(\+216|216)?[0-9]{8}$',
        message="Le numéro de téléphone doit être au format tunisien: +21612345678 ou 21612345678"
    )
    
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[phone_regex],
        verbose_name="Numéro de téléphone"
    )
    first_name = models.CharField(max_length=50, verbose_name="Prénom")
    last_name = models.CharField(max_length=50, verbose_name="Nom")
    email = models.EmailField(blank=True, null=True, verbose_name="Adresse email")
    birth_date = models.DateField(verbose_name="Date de naissance", null=True, blank=True)
    birth_place = models.CharField(max_length=100, verbose_name="Lieu de naissance", null=True, blank=True)
    address = models.TextField(verbose_name="Adresse", null=True, blank=True)
    cin = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="Numéro CIN")
    
    # Photo de profil
    profile_photo = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name="Photo de profil"
    )
    
    # Informations professionnelles
    role = models.CharField(
        max_length=20,
        choices=[
            ('arbitre', 'Arbitre'),
            ('assistant', 'Assistant'),
        ],
        default='arbitre',
        verbose_name="Rôle"
    )
    grade = models.CharField(
        max_length=20,
        choices=[
            ('candidat', 'Candidat'),
            ('3eme_serie', '3ème Série'),
            ('2eme_serie', '2ème Série'),
            ('1ere_serie', '1ère Série'),
            ('federale', 'Fédérale'),
        ],
        default='candidat',
        verbose_name="Grade d'arbitrage"
    )
    ligue = models.ForeignKey(
        LigueArbitrage,
        on_delete=models.CASCADE,
        verbose_name="Ligue d'arbitrage",
        null=True,
        blank=True
    )
    
    # Statut du compte
    is_active = models.BooleanField(default=True, verbose_name="Compte actif")
    is_staff = models.BooleanField(default=False, verbose_name="Membre du staff")
    is_superuser = models.BooleanField(default=False, verbose_name="Super utilisateur")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    last_login = models.DateTimeField(auto_now=True, verbose_name="Dernière connexion")
    
    # Gestionnaire personnalisé
    objects = ArbitreManager()
    
    # Configuration pour l'authentification
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    # Résolution des conflits de permissions
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='arbitre_user_set',
        related_query_name='arbitre_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='arbitre_user_set',
        related_query_name='arbitre_user',
    )
    
    class Meta:
        verbose_name = "Arbitre"
        verbose_name_plural = "Arbitres"
        ordering = ['-date_joined']
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.phone_number}) - {self.get_grade_display()}"
    
    def get_grade_display(self):
        grade_choices = dict(self._meta.get_field('grade').choices)
        return grade_choices.get(self.grade, self.grade)

# ============================================================================
# MODÈLE COMMISSAIRE
# ============================================================================

class CommissaireManager(BaseUserManager):
    """Gestionnaire personnalisé pour le modèle Commissaire"""
    
    def create_user(self, phone_number, first_name, last_name, password=None, **extra_fields):
        """Créer un utilisateur commissaire normal"""
        if not phone_number:
            raise ValueError('Le numéro de téléphone est obligatoire')
        if not first_name:
            raise ValueError('Le prénom est obligatoire')
        if not last_name:
            raise ValueError('Le nom est obligatoire')
        
        user = self.model(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, first_name, last_name, password=None, **extra_fields):
        """Créer un super utilisateur commissaire"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le super utilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le super utilisateur doit avoir is_superuser=True.')
        
        return self.create_user(phone_number, first_name, last_name, password, **extra_fields)

class Commissaire(AbstractBaseUser, PermissionsMixin):
    """Modèle pour les commissaires de match (mobile uniquement)"""
    
    # Validation du numéro de téléphone tunisien
    phone_regex = RegexValidator(
        regex=r'^(\+216|216)?[0-9]{8}$',
        message="Le numéro de téléphone doit être au format tunisien: +21612345678 ou 21612345678"
    )
    
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[phone_regex],
        verbose_name="Numéro de téléphone"
    )
    first_name = models.CharField(max_length=50, verbose_name="Prénom")
    last_name = models.CharField(max_length=50, verbose_name="Nom")
    email = models.EmailField(blank=True, null=True, verbose_name="Adresse email")
    birth_date = models.DateField(verbose_name="Date de naissance", null=True, blank=True)
    birth_place = models.CharField(max_length=100, verbose_name="Lieu de naissance", null=True, blank=True)
    address = models.TextField(verbose_name="Adresse", null=True, blank=True)
    cin = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="Numéro CIN")
    
    # Informations professionnelles
    grade = models.CharField(
        max_length=20,
        choices=[
            ('debutant', 'Débutant'),
            ('regional', 'Régional'),
            ('national', 'National'),
            ('international', 'International'),
        ],
        default='debutant',
        verbose_name="Grade"
    )
    ligue = models.ForeignKey(
        LigueArbitrage,
        on_delete=models.CASCADE,
        verbose_name="Ligue d'arbitrage",
        null=True,
        blank=True
    )
    
    # Spécificités du commissaire
    specialite = models.CharField(
        max_length=50,
        choices=[
            ('commissaire_match', 'Commissaire de Match'),
            ('delegue_technique', 'Délégué Technique'),
            ('observateur', 'Observateur'),
            ('superviseur', 'Superviseur'),
        ],
        default='commissaire_match',
        verbose_name="Spécialité"
    )
    
    # Statut du compte
    is_active = models.BooleanField(default=True, verbose_name="Compte actif")
    is_staff = models.BooleanField(default=False, verbose_name="Membre du staff")
    is_superuser = models.BooleanField(default=False, verbose_name="Super utilisateur")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    last_login = models.DateTimeField(auto_now=True, verbose_name="Dernière connexion")
    
    # Gestionnaire personnalisé
    objects = CommissaireManager()
    
    # Configuration pour l'authentification
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    # Résolution des conflits de permissions
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='commissaire_user_set',
        related_query_name='commissaire_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='commissaire_user_set',
        related_query_name='commissaire_user',
    )
    
    class Meta:
        verbose_name = "Commissaire"
        verbose_name_plural = "Commissaires"
        ordering = ['-date_joined']
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.phone_number}) - {self.get_specialite_display()}"
    
    def get_specialite_display(self):
        specialite_choices = dict(self._meta.get_field('specialite').choices)
        return specialite_choices.get(self.specialite, self.specialite)

# ============================================================================
# MODÈLE ADMIN
# ============================================================================

class AdminManager(BaseUserManager):
    """Gestionnaire personnalisé pour le modèle Admin"""
    
    def create_user(self, phone_number, email, first_name, last_name, password=None, **extra_fields):
        """Créer un utilisateur admin normal"""
        if not phone_number:
            raise ValueError('Le numéro de téléphone est obligatoire')
        if not email:
            raise ValueError('L\'email est obligatoire')
        if not first_name:
            raise ValueError('Le prénom est obligatoire')
        if not last_name:
            raise ValueError('Le nom est obligatoire')
        
        email = self.normalize_email(email)
        user = self.model(
            phone_number=phone_number,
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, email, first_name, last_name, password=None, **extra_fields):
        """Créer un super administrateur"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'super_admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le super utilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le super utilisateur doit avoir is_superuser=True.')
        
        return self.create_user(phone_number, email, first_name, last_name, password, **extra_fields)

class Admin(AbstractBaseUser, PermissionsMixin):
    """Modèle pour les administrateurs du système web"""
    
    USER_TYPE_CHOICES = [
        ('admin', 'Administrateur'),
        ('super_admin', 'Super Administrateur'),
        ('moderateur', 'Modérateur'),
    ]
    
    # Validation du numéro de téléphone tunisien
    phone_regex = RegexValidator(
        regex=r'^(\+216|216)?[0-9]{8}$',
        message="Le numéro de téléphone doit être au format tunisien: +21612345678 ou 21612345678"
    )
    
    phone_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[phone_regex],
        verbose_name="Numéro de téléphone"
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Adresse email"
    )
    first_name = models.CharField(max_length=50, verbose_name="Prénom")
    last_name = models.CharField(max_length=50, verbose_name="Nom")
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='admin',
        verbose_name="Type d'utilisateur"
    )
    
    # Informations supplémentaires
    department = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Département"
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Poste"
    )
    
    # Statut du compte
    is_active = models.BooleanField(default=True, verbose_name="Compte actif")
    is_staff = models.BooleanField(default=True, verbose_name="Membre du staff")
    is_superuser = models.BooleanField(default=False, verbose_name="Super administrateur")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    last_login = models.DateTimeField(auto_now=True, verbose_name="Dernière connexion")
    
    # Gestionnaire personnalisé
    objects = AdminManager()
    
    # Configuration pour l'authentification
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    
    # Résolution des conflits de permissions
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='admin_user_set',
        related_query_name='admin_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='admin_user_set',
        related_query_name='admin_user',
    )
    
    class Meta:
        verbose_name = "Administrateur"
        verbose_name_plural = "Administrateurs"
        ordering = ['-date_joined']
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name
    
    def get_user_type_display(self):
        return dict(self.USER_TYPE_CHOICES).get(self.user_type, self.user_type)
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.phone_number}) - {self.get_user_type_display()}"

# ============================================================================
# NOTIFICATIONS PUSH
# ============================================================================

class PushSubscription(models.Model):
    """Modèle pour les abonnements push des arbitres"""
    
    arbitre = models.ForeignKey(
        Arbitre,
        on_delete=models.CASCADE,
        related_name='push_subscriptions',
        verbose_name="Arbitre"
    )
    
    endpoint = models.URLField(verbose_name="Endpoint de notification")
    p256dh = models.TextField(verbose_name="Clé publique P-256 DH")
    auth = models.TextField(verbose_name="Clé d'authentification")
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    is_active = models.BooleanField(default=True, verbose_name="Abonnement actif")
    last_used = models.DateTimeField(auto_now=True, verbose_name="Dernière utilisation")
    
    class Meta:
        verbose_name = "Abonnement Push"
        verbose_name_plural = "Abonnements Push"
        unique_together = ['arbitre', 'endpoint']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Push pour {self.arbitre.get_full_name()}"
    
    @property
    def subscription_info(self):
        """Retourne les informations d'abonnement au format Web Push"""
        return {
            'endpoint': self.endpoint,
            'keys': {
                'p256dh': self.p256dh,
                'auth': self.auth
            }
        }

# ============================================================================
# FIREBASE CLOUD MESSAGING (FCM)
# ============================================================================

class FCMToken(models.Model):
    """Modèle pour stocker les tokens FCM des appareils mobiles"""
    
    DEVICE_TYPE_CHOICES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web'),
    ]
    
    # Relations avec les utilisateurs (peut être un Arbitre, Commissaire ou Admin)
    arbitre = models.ForeignKey(
        Arbitre,
        on_delete=models.CASCADE,
        related_name='fcm_tokens',
        null=True,
        blank=True,
        verbose_name="Arbitre"
    )
    commissaire = models.ForeignKey(
        Commissaire,
        on_delete=models.CASCADE,
        related_name='fcm_tokens',
        null=True,
        blank=True,
        verbose_name="Commissaire"
    )
    admin = models.ForeignKey(
        Admin,
        on_delete=models.CASCADE,
        related_name='fcm_tokens',
        null=True,
        blank=True,
        verbose_name="Administrateur"
    )
    
    # Informations du token FCM
    token = models.CharField(max_length=255, unique=True, verbose_name="Token FCM")
    device_type = models.CharField(
        max_length=20,
        choices=DEVICE_TYPE_CHOICES,
        verbose_name="Type d'appareil"
    )
    device_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID de l'appareil")
    app_version = models.CharField(max_length=50, blank=True, null=True, verbose_name="Version de l'app")
    
    # Statut et métadonnées
    is_active = models.BooleanField(default=True, verbose_name="Token actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    last_used = models.DateTimeField(auto_now=True, verbose_name="Dernière utilisation")
    
    class Meta:
        db_table = 'fcm_tokens'
        verbose_name = "Token FCM"
        verbose_name_plural = "Tokens FCM"
        unique_together = ['token']
        ordering = ['-created_at']
    
    def __str__(self):
        user_info = self.get_user_info()
        return f"{user_info} - {self.device_type} - {self.token[:20]}..."
    
    def get_user_info(self):
        """Retourne les informations de l'utilisateur associé"""
        if self.arbitre:
            return f"Arbitre: {self.arbitre.get_full_name()}"
        elif self.commissaire:
            return f"Commissaire: {self.commissaire.get_full_name()}"
        elif self.admin:
            return f"Admin: {self.admin.get_full_name()}"
        return "Utilisateur inconnu"
    
    def get_user(self):
        """Retourne l'utilisateur associé (Arbitre, Commissaire ou Admin)"""
        if self.arbitre:
            return self.arbitre
        elif self.commissaire:
            return self.commissaire
        elif self.admin:
            return self.admin
        return None
    
    def clean(self):
        """Validation: un token doit être associé à exactement un utilisateur"""
        from django.core.exceptions import ValidationError
        
        user_count = sum([
            bool(self.arbitre),
            bool(self.commissaire),
            bool(self.admin)
        ])
        
        if user_count != 1:
            raise ValidationError("Un token FCM doit être associé à exactement un utilisateur.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

# ============================================================================
# NOTIFICATIONS DE DÉSIGNATION
# ============================================================================

class NotificationDesignation(models.Model):
    """Modèle pour l'historique des notifications de désignation d'arbitres"""
    
    DESIGNATION_TYPE_CHOICES = [
        ('arbitre_principal', 'Arbitre Principal'),
        ('arbitre_assistant_1', 'Assistant 1'),
        ('arbitre_assistant_2', 'Assistant 2'),
        ('arbitre_quatrieme', 'Quatrième Arbitre'),
        ('commissaire_match', 'Commissaire de Match'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Envoyée'),
        ('delivered', 'Livrée'),
        ('read', 'Lue'),
        ('failed', 'Échouée'),
    ]
    
    # Relations
    arbitre = models.ForeignKey(
        Arbitre,
        on_delete=models.CASCADE,
        related_name='designation_notifications',
        verbose_name="Arbitre"
    )
    
    # Informations du match
    match_id = models.IntegerField(verbose_name="ID du match")
    match_nom = models.CharField(max_length=200, verbose_name="Nom du match")
    match_date = models.DateTimeField(verbose_name="Date du match")
    match_lieu = models.CharField(max_length=200, verbose_name="Lieu du match")
    
    # Type de désignation
    designation_type = models.CharField(
        max_length=30,
        choices=DESIGNATION_TYPE_CHOICES,
        verbose_name="Type de désignation"
    )
    
    # Contenu de la notification
    title = models.CharField(max_length=200, verbose_name="Titre")
    message = models.TextField(verbose_name="Message")
    
    # Statut et métadonnées
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='sent',
        verbose_name="Statut"
    )
    is_read = models.BooleanField(default=False, verbose_name="Notification lue")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Date d'envoi")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de lecture")
    
    # Données supplémentaires
    fcm_response = models.JSONField(null=True, blank=True, verbose_name="Réponse FCM")
    error_message = models.TextField(blank=True, verbose_name="Message d'erreur")
    
    class Meta:
        db_table = 'notification_designations'
        verbose_name = "Notification de Désignation"
        verbose_name_plural = "Notifications de Désignation"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['arbitre', '-created_at']),
            models.Index(fields=['match_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.arbitre.get_full_name()} - {self.match_nom} - {self.get_designation_type_display()}"
    
    def mark_as_read(self):
        """Marquer la notification comme lue"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.status = 'read'
            self.save(update_fields=['is_read', 'read_at', 'status'])
    
    def mark_as_delivered(self):
        """Marquer la notification comme livrée"""
        if self.status == 'sent':
            self.status = 'delivered'
            self.save(update_fields=['status'])
    
    def mark_as_failed(self, error_message=""):
        """Marquer la notification comme échouée"""
        self.status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message'])
    
    @property
    def time_since_created(self):
        """Temps écoulé depuis la création"""
        return timezone.now() - self.created_at
    
    @property
    def is_recent(self):
        """Vérifier si la notification est récente (moins de 24h)"""
        return self.time_since_created.total_seconds() < 86400  # 24 heures

# ============================================================================
# MODÈLE EXCUSE ARBITRE
# ============================================================================

class ExcuseArbitre(models.Model):
    """Modèle pour les excuses d'arbitres"""
    
    # Statuts possibles
    STATUS_CHOICES = [
        ('en_attente', 'En Attente'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('annulee', 'Annulée'),
    ]
    
    # Relation avec l'arbitre
    arbitre = models.ForeignKey(
        Arbitre,
        on_delete=models.CASCADE,
        related_name='excuses',
        verbose_name="Arbitre"
    )
    
    # Informations de l'excuse
    date_debut = models.DateField(
        verbose_name="Date de début",
        help_text="Date de début de l'indisponibilité"
    )
    date_fin = models.DateField(
        verbose_name="Date de fin",
        help_text="Date de fin de l'indisponibilité"
    )
    cause = models.TextField(
        verbose_name="Cause de l'excuse",
        help_text="Description détaillée de la raison de l'excuse"
    )
    piece_jointe = models.ImageField(
        upload_to='excuses/',
        blank=True,
        null=True,
        verbose_name="Pièce jointe",
        help_text="Document justificatif (optionnel)"
    )
    
    # Statut et gestion
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='en_attente',
        verbose_name="Statut"
    )
    
    # Commentaires de l'administration
    commentaire_admin = models.TextField(
        blank=True,
        null=True,
        verbose_name="Commentaire de l'administration"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    # Traitement
    traite_par = models.ForeignKey(
        Admin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='excuses_traitees',
        verbose_name="Traité par"
    )
    traite_le = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Traité le"
    )
    
    class Meta:
        verbose_name = "Excuse d'Arbitre"
        verbose_name_plural = "Excuses d'Arbitres"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['arbitre', 'status']),
            models.Index(fields=['date_debut', 'date_fin']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Excuse de {self.arbitre.get_full_name()} - {self.date_debut} au {self.date_fin}"
    
    def get_status_display(self):
        """Retourner le statut formaté"""
        status_choices = dict(self.STATUS_CHOICES)
        return status_choices.get(self.status, self.status)
    
    def get_duree(self):
        """Calculer la durée de l'excuse en jours"""
        return (self.date_fin - self.date_debut).days + 1
    
    def is_en_cours(self):
        """Vérifier si l'excuse est en cours (date actuelle entre début et fin)"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.date_debut <= today <= self.date_fin
    
    def is_passee(self):
        """Vérifier si l'excuse est passée"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.date_fin < today
    
    def is_future(self):
        """Vérifier si l'excuse est future"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.date_debut > today
    
    def accepter(self, admin_user, commentaire=None):
        """Accepter l'excuse"""
        self.status = 'acceptee'
        self.traite_par = admin_user
        self.traite_le = timezone.now()
        if commentaire:
            self.commentaire_admin = commentaire
        self.save()
    
    def refuser(self, admin_user, commentaire=None):
        """Refuser l'excuse"""
        self.status = 'refusee'
        self.traite_par = admin_user
        self.traite_le = timezone.now()
        if commentaire:
            self.commentaire_admin = commentaire
        self.save()
    
    def annuler(self, admin_user=None, commentaire=None):
        """Annuler l'excuse"""
        self.status = 'annulee'
        if admin_user:
            self.traite_par = admin_user
            self.traite_le = timezone.now()
        if commentaire:
            self.commentaire_admin = commentaire
        self.save()
    
    @property
    def can_be_modified(self):
        """Vérifier si l'excuse peut être modifiée (seulement si en attente)"""
        return self.status == 'en_attente'
    
    @property
    def can_be_cancelled(self):
        """Vérifier si l'excuse peut être annulée"""
        return self.status in ['en_attente', 'acceptee'] and not self.is_passee()

# ============================================================================
# MODÈLE POUR LA RÉINITIALISATION DE MOT DE PASSE
# ============================================================================

class PasswordResetToken(models.Model):
    """Modèle pour les tokens de réinitialisation de mot de passe"""
    
    # Relations avec les utilisateurs (peut être un Arbitre, Commissaire ou Admin)
    arbitre = models.ForeignKey(
        Arbitre,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        null=True,
        blank=True,
        verbose_name="Arbitre"
    )
    commissaire = models.ForeignKey(
        Commissaire,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        null=True,
        blank=True,
        verbose_name="Commissaire"
    )
    admin = models.ForeignKey(
        Admin,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        null=True,
        blank=True,
        verbose_name="Administrateur"
    )
    
    # Token et métadonnées
    token = models.CharField(max_length=255, unique=True, verbose_name="Token de réinitialisation")
    otp_code = models.CharField(max_length=6, verbose_name="Code OTP")
    email = models.EmailField(verbose_name="Adresse email")
    
    # Statut et timestamps
    is_used = models.BooleanField(default=False, verbose_name="Token utilisé")
    otp_verified = models.BooleanField(default=False, verbose_name="OTP vérifié")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    expires_at = models.DateTimeField(verbose_name="Date d'expiration")
    used_at = models.DateTimeField(null=True, blank=True, verbose_name="Date d'utilisation")
    otp_verified_at = models.DateTimeField(null=True, blank=True, verbose_name="Date de vérification OTP")
    
    # Informations de sécurité
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Adresse IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    
    class Meta:
        db_table = 'password_reset_tokens'
        verbose_name = "Token de Réinitialisation"
        verbose_name_plural = "Tokens de Réinitialisation"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['email']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_used']),
        ]
    
    def __str__(self):
        user_info = self.get_user_info()
        return f"Token pour {user_info} - {self.email}"
    
    def get_user_info(self):
        """Retourne les informations de l'utilisateur associé"""
        if self.arbitre:
            return f"Arbitre: {self.arbitre.get_full_name()}"
        elif self.commissaire:
            return f"Commissaire: {self.commissaire.get_full_name()}"
        elif self.admin:
            return f"Admin: {self.admin.get_full_name()}"
        return "Utilisateur inconnu"
    
    def get_user(self):
        """Retourne l'utilisateur associé (Arbitre, Commissaire ou Admin)"""
        if self.arbitre:
            return self.arbitre
        elif self.commissaire:
            return self.commissaire
        elif self.admin:
            return self.admin
        return None
    
    def is_expired(self):
        """Vérifier si le token a expiré"""
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Vérifier si le token est valide (non utilisé et non expiré)"""
        return not self.is_used and not self.is_expired()
    
    def is_otp_valid(self):
        """Vérifier si le token est valide pour la vérification OTP"""
        return not self.is_used and not self.is_expired() and not self.otp_verified
    
    def mark_as_used(self):
        """Marquer le token comme utilisé"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])
    
    def mark_otp_as_verified(self):
        """Marquer l'OTP comme vérifié"""
        self.otp_verified = True
        self.otp_verified_at = timezone.now()
        self.save(update_fields=['otp_verified', 'otp_verified_at'])
    
    def clean(self):
        """Validation: un token doit être associé à exactement un utilisateur"""
        from django.core.exceptions import ValidationError
        
        user_count = sum([
            bool(self.arbitre),
            bool(self.commissaire),
            bool(self.admin)
        ])
        
        if user_count != 1:
            raise ValidationError("Un token de réinitialisation doit être associé à exactement un utilisateur.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def create_for_user(cls, user, email, ip_address=None, user_agent=None):
        """Créer un nouveau token de réinitialisation pour un utilisateur"""
        import secrets
        import random
        from django.conf import settings
        from datetime import timedelta
        
        # Générer un token sécurisé
        token = secrets.token_urlsafe(32)
        
        # Générer un code OTP à 6 chiffres
        otp_code = str(random.randint(100000, 999999))
        
        # Calculer la date d'expiration (5 minutes par défaut pour la sécurité)
        expiry_minutes = getattr(settings, 'PASSWORD_RESET_SETTINGS', {}).get('TOKEN_EXPIRY_MINUTES', 5)
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        
        # Déterminer le type d'utilisateur et créer le token
        token_data = {
            'token': token,
            'otp_code': otp_code,
            'email': email,
            'expires_at': expires_at,
            'ip_address': ip_address,
            'user_agent': user_agent,
        }
        
        if isinstance(user, Arbitre):
            token_data['arbitre'] = user
        elif isinstance(user, Commissaire):
            token_data['commissaire'] = user
        elif isinstance(user, Admin):
            token_data['admin'] = user
        else:
            raise ValueError("Type d'utilisateur non supporté")
        
        # Désactiver tous les tokens précédents pour cet utilisateur
        cls.objects.filter(
            **{type(user).__name__.lower(): user},
            is_used=False
        ).update(is_used=True, used_at=timezone.now())
        
        return cls.objects.create(**token_data)
    
    @classmethod
    def get_valid_token(cls, token):
        """Récupérer un token valide"""
        try:
            token_obj = cls.objects.get(token=token)
            if token_obj.is_valid():
                return token_obj
            return None
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_valid_otp_token(cls, token):
        """Récupérer un token valide pour la vérification OTP"""
        try:
            token_obj = cls.objects.get(token=token)
            if token_obj.is_otp_valid():
                return token_obj
            return None
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def check_rate_limit(cls, email):
        """Vérifier la limitation de taux pour un email"""
        from django.conf import settings
        from datetime import timedelta
        
        max_attempts = getattr(settings, 'PASSWORD_RESET_SETTINGS', {}).get('MAX_ATTEMPTS_PER_HOUR', 3)
        
        # Compter les tentatives dans la dernière heure
        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_attempts = cls.objects.filter(
            email=email,
            created_at__gte=one_hour_ago
        ).count()
        
        return recent_attempts < max_attempts
    
    @classmethod
    def cleanup_old_tokens(cls):
        """Nettoyer automatiquement les anciens tokens"""
        from django.conf import settings
        from datetime import timedelta
        
        cleanup_hours = getattr(settings, 'PASSWORD_RESET_SETTINGS', {}).get('AUTO_CLEANUP_HOURS', 1)
        cutoff_time = timezone.now() - timedelta(hours=cleanup_hours)
        
        # Supprimer les tokens expirés ou anciens
        from django.db import models as db_models
        deleted_count = cls.objects.filter(
            db_models.Q(expires_at__lt=timezone.now()) | 
            db_models.Q(created_at__lt=cutoff_time)
        ).delete()[0]
        
        return deleted_count

