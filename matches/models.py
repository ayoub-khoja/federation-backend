"""
Modèles pour la gestion des matchs
"""
from django.db import models
from django.conf import settings
from django.utils import timezone

class TypeMatch(models.Model):
    """Modèle pour les types de match"""
    
    nom = models.CharField(max_length=100, verbose_name="Nom du type de match")
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    ordre = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    class Meta:
        verbose_name = "Type de match"
        verbose_name_plural = "Types de match"
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return self.nom

class Categorie(models.Model):
    """Modèle pour les catégories de match"""
    
    nom = models.CharField(max_length=50, verbose_name="Nom de la catégorie")
    code = models.CharField(max_length=10, unique=True, verbose_name="Code")
    age_min = models.IntegerField(null=True, blank=True, verbose_name="Âge minimum")
    age_max = models.IntegerField(null=True, blank=True, verbose_name="Âge maximum")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    ordre = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return self.nom

class Match(models.Model):
    """Modèle pour représenter un match"""
    
    # Statuts du match
    STATUS_CHOICES = [
        ('scheduled', 'Programmé'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
        ('postponed', 'Reporté'),
    ]
    
    # Informations de base
    type_match = models.ForeignKey(
        TypeMatch,
        on_delete=models.CASCADE,
        verbose_name="Type de match",
        null=True,
        blank=True
    )
    categorie = models.ForeignKey(
        Categorie,
        on_delete=models.CASCADE,
        verbose_name="Catégorie",
        null=True,
        blank=True
    )
    
    # Lieu et date
    stadium = models.CharField(max_length=100, verbose_name="Stade")
    match_date = models.DateField(verbose_name="Date du match")
    match_time = models.TimeField(verbose_name="Heure du match")
    
    # Équipes
    home_team = models.CharField(max_length=50, verbose_name="Équipe domicile")
    away_team = models.CharField(max_length=50, verbose_name="Équipe visiteur")
    
    # Score (optionnel, rempli après le match)
    home_score = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Score domicile"
    )
    away_score = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Score visiteur"
    )
    
    # Rôle de l'arbitre dans ce match
    ROLE_CHOICES = [
        ('arbitre_principal', 'Arbitre Principal'),
        ('arbitre_assistant1', '1er Arbitre Assistant'),
        ('arbitre_assistant2', '2ème Arbitre Assistant'),
        ('quatrieme_arbitre', '4ème Arbitre'),
        ('arbitre_video', 'Arbitre VAR'),
        ('arbitre_assistant_video', 'Assistant VAR'),
    ]
    
    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default='arbitre_principal',
        verbose_name="Rôle de l'arbitre"
    )
    
    # Description
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description du match"
    )
    
    # Feuille de match
    match_sheet = models.FileField(
        upload_to='match_sheets/',
        null=True,
        blank=True,
        verbose_name="Feuille de match"
    )
    
    # Arbitre assigné
    referee = models.ForeignKey(
        'accounts.Arbitre',
        on_delete=models.CASCADE,
        related_name='matches',
        verbose_name="Arbitre"
    )
    
    # Statut et métadonnées
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name="Statut"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    # Champs pour les rapports post-match
    match_report = models.TextField(
        blank=True,
        null=True,
        verbose_name="Rapport de match"
    )
    incidents = models.TextField(
        blank=True,
        null=True,
        verbose_name="Incidents"
    )
    
    class Meta:
        verbose_name = "Match"
        verbose_name_plural = "Matchs"
        ordering = ['-match_date', '-match_time']
        
    def __str__(self):
        type_name = self.type_match.nom if self.type_match else "Type non défini"
        categorie_name = self.categorie.nom if self.categorie else "Catégorie non définie"
        return f"{self.home_team} vs {self.away_team} - {self.match_date} ({type_name} - {categorie_name})"
    
    @property
    def is_completed(self):
        """Vérifie si le match est terminé"""
        return self.status == 'completed'
    
    @property
    def has_score(self):
        """Vérifie si le score a été saisi"""
        return self.home_score is not None and self.away_score is not None
    
    @property
    def score_display(self):
        """Affiche le score du match"""
        if self.has_score:
            return f"{self.home_score} - {self.away_score}"
        return "Score non disponible"

class MatchEvent(models.Model):
    """Modèle pour les événements du match (cartons, buts, etc.)"""
    
    EVENT_TYPE_CHOICES = [
        ('yellow_card', 'Carton jaune'),
        ('red_card', 'Carton rouge'),
        ('goal', 'But'),
        ('penalty', 'Pénalty'),
        ('substitution', 'Remplacement'),
        ('other', 'Autre'),
    ]
    
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name="Match"
    )
    
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        verbose_name="Type d'événement"
    )
    
    team = models.CharField(
        max_length=50,
        verbose_name="Équipe concernée"
    )
    
    player_name = models.CharField(
        max_length=100,
        verbose_name="Nom du joueur"
    )
    
    minute = models.PositiveIntegerField(
        verbose_name="Minute de l'événement"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Événement de match"
        verbose_name_plural = "Événements de match"
        ordering = ['minute']
    
    def __str__(self):
        return f"{self.get_event_type_display()} - {self.player_name} ({self.minute}')"


class Designation(models.Model):
    """Modèle pour les désignations d'arbitrage"""
    
    # Types de désignation
    TYPE_CHOICES = [
        ('arbitre_principal', 'Arbitre Principal'),
        ('arbitre_assistant1', '1er Arbitre Assistant'),
        ('arbitre_assistant2', '2ème Arbitre Assistant'),
        ('quatrieme_arbitre', '4ème Arbitre'),
        ('arbitre_video', 'Arbitre VAR'),
        ('arbitre_assistant_video', 'Assistant VAR'),
    ]
    
    # Statuts de la désignation
    STATUS_CHOICES = [
        ('proposed', 'Proposée'),
        ('accepted', 'Acceptée'),
        ('declined', 'Refusée'),
        ('confirmed', 'Confirmée'),
        ('cancelled', 'Annulée'),
    ]
    
    # Match concerné
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='designations',
        verbose_name="Match"
    )
    
    # Arbitre désigné
    arbitre = models.ForeignKey(
        'accounts.Arbitre',
        on_delete=models.CASCADE,
        related_name='designations',
        verbose_name="Arbitre"
    )
    
    # Type de désignation
    type_designation = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        verbose_name="Type de désignation"
    )
    
    # Statut de la désignation
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='proposed',
        verbose_name="Statut"
    )
    
    # Date de désignation
    date_designation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de désignation"
    )
    
    # Date de réponse de l'arbitre
    date_reponse = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de réponse"
    )
    
    # Commentaires
    commentaires = models.TextField(
        blank=True,
        null=True,
        verbose_name="Commentaires"
    )
    
    # Raison du refus (si applicable)
    raison_refus = models.TextField(
        blank=True,
        null=True,
        verbose_name="Raison du refus"
    )
    
    # Notifications envoyées
    notification_envoyee = models.BooleanField(
        default=False,
        verbose_name="Notification envoyée"
    )
    
    # Date d'envoi de la notification
    date_notification = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date d'envoi de la notification"
    )
    
    class Meta:
        verbose_name = "Désignation d'arbitrage"
        verbose_name_plural = "Désignations d'arbitrage"
        unique_together = ['match', 'arbitre', 'type_designation']
        ordering = ['-date_designation']
    
    def __str__(self):
        return f"{self.arbitre.get_full_name()} - {self.get_type_designation_display()} - {self.match}"
    
    @property
    def is_accepted(self):
        """Vérifie si la désignation est acceptée"""
        return self.status == 'accepted'
    
    @property
    def is_declined(self):
        """Vérifie si la désignation est refusée"""
        return self.status == 'declined'
    
    @property
    def is_pending(self):
        """Vérifie si la désignation est en attente de réponse"""
        return self.status == 'proposed'
    
    def accepter(self):
        """Accepter la désignation"""
        self.status = 'accepted'
        self.date_reponse = timezone.now()
        self.save()
    
    def refuser(self, raison=None):
        """Refuser la désignation"""
        self.status = 'declined'
        self.date_reponse = timezone.now()
        if raison:
            self.raison_refus = raison
        self.save()
    
    def confirmer(self):
        """Confirmer la désignation"""
        self.status = 'confirmed'
        self.save()
    
    def annuler(self):
        """Annuler la désignation"""
        self.status = 'cancelled'
        self.save()
    
    def marquer_notification_envoyee(self):
        """Marquer que la notification a été envoyée"""
        self.notification_envoyee = True
        self.date_notification = timezone.now()
        self.save()


class TarificationMatch(models.Model):
    """Modèle pour les tarifs des matchs selon le type et le rôle"""
    
    # Types de compétition
    COMPETITION_CHOICES = [
        ('championnat', 'Championnat'),
        ('coupe_tunisie_seniors', 'Coupe de Tunisie Seniors'),
        ('coupe_tunisie_jeunes', 'Coupe de Tunisie Jeunes'),
        ('super_coupe', 'Super Coupe de Tunisie'),
        ('matchs_amicaux', 'Matchs Amicaux'),
    ]
    
    # Divisions/Catégories
    DIVISION_CHOICES = [
        ('seniors', 'Seniors'),
        ('jeunes', 'Jeunes'),
        ('feminin', 'Féminin'),
        ('cadettes', 'Cadettes'),
    ]
    
    # Types de match
    TYPE_MATCH_CHOICES = [
        # Championnat
        ('ligue1', 'Ligue 1'),
        ('ligue2', 'Ligue 2'),
        ('c1', 'C1'),
        ('c2', 'C2'),
        ('ff', 'FF'),
        ('reg', 'Régional'),
        # Coupe de Tunisie Seniors
        ('1_8', '1/8 de finale'),
        ('1_4', '1/4 de finale'),
        ('1_2', '1/2 de finale'),
        ('finale', 'Finale'),
        # Coupe de Tunisie Jeunes
        ('u21_u19', 'U21/U19'),
        ('u17_u16_u15_u14', 'U17/U16/U15/U14'),
        ('feminin_cadettes', 'Féminin Cadettes'),
        # Super Coupe
        ('super_coupe_seniors', 'Super Coupe Seniors'),
        # Matchs Amicaux
        ('seniors_amical', 'Seniors Amical'),
        ('u21_u19_amical', 'U21/U19 Amical'),
        ('u15_u14_amical', 'U15/U14 Amical'),
        ('eq_nat_vs_club_seniors', 'Équipe Nationale vs Club Seniors'),
        ('eq_nat_vs_club_u21_u19', 'Équipe Nationale vs Club U21/U19'),
        ('eq_nat_vs_club_u15_u14', 'Équipe Nationale vs Club U15/U14'),
    ]
    
    # Rôles d'arbitrage
    ROLE_CHOICES = [
        ('arbitre', 'Arbitre'),
        ('assistant', 'Assistant'),
        ('4eme_arbitre', '4ème Arbitre'),
        ('commissaire', 'Commissaire'),
    ]
    
    # Champs principaux
    competition = models.CharField(
        max_length=50,
        choices=COMPETITION_CHOICES,
        verbose_name="Compétition"
    )
    
    division = models.CharField(
        max_length=20,
        choices=DIVISION_CHOICES,
        null=True,
        blank=True,
        verbose_name="Division"
    )
    
    type_match = models.CharField(
        max_length=50,
        choices=TYPE_MATCH_CHOICES,
        verbose_name="Type de match"
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name="Rôle"
    )
    
    # Tarif en dinars tunisiens
    tarif = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        verbose_name="Tarif (TND)"
    )
    
    # Devise (par défaut TND)
    devise = models.CharField(
        max_length=3,
        default='TND',
        verbose_name="Devise"
    )
    
    # Statut actif/inactif
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "Tarification de match"
        verbose_name_plural = "Tarifications de matchs"
        unique_together = ['competition', 'division', 'type_match', 'role']
        ordering = ['competition', 'division', 'type_match', 'role']
    
    def __str__(self):
        division_str = f" - {self.get_division_display()}" if self.division else ""
        return f"{self.get_competition_display()}{division_str} - {self.get_type_match_display()} - {self.get_role_display()}: {self.tarif} {self.devise}"
    
    @property
    def tarif_formatted(self):
        """Retourne le tarif formaté avec la devise"""
        return f"{self.tarif} {self.devise}"


class ExcuseArbitre(models.Model):
    """Modèle pour les excuses d'arbitres"""
    
    nom_arbitre = models.CharField(max_length=100, verbose_name="Nom de l'arbitre")
    prenom_arbitre = models.CharField(max_length=100, verbose_name="Prénom de l'arbitre")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    cause = models.TextField(verbose_name="Cause de l'excuse")
    piece_jointe = models.FileField(
        upload_to='excuses/',
        blank=True,
        null=True,
        verbose_name="Pièce jointe"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    
    class Meta:
        verbose_name = "Excuse d'arbitre"
        verbose_name_plural = "Excuses d'arbitres"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.prenom_arbitre} {self.nom_arbitre} - {self.date_debut} au {self.date_fin}"
    
    def clean(self):
        """Validation des dates"""
        from django.core.exceptions import ValidationError
        if self.date_debut and self.date_fin and self.date_debut > self.date_fin:
            raise ValidationError("La date de début ne peut pas être postérieure à la date de fin")





