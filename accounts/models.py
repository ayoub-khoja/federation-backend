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

