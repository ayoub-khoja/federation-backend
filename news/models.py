from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class News(models.Model):
    """Modèle pour les actualités de l'accueil arbitres"""
    
    # Titres en français et arabe
    title_fr = models.CharField(max_length=200, verbose_name="Titre en français")
    title_ar = models.CharField(max_length=200, verbose_name="Titre en arabe")
    
    # Contenu en français et arabe
    content_fr = models.TextField(verbose_name="Contenu en français")
    content_ar = models.TextField(verbose_name="Contenu en arabe")
    
    # Média optionnel
    image = models.ImageField(upload_to='news/images/', blank=True, null=True, verbose_name="Image")
    video = models.FileField(upload_to='news/videos/', blank=True, null=True, verbose_name="Vidéo")
    
    # Métadonnées - Auteur générique (User ou Admin)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="Type d'auteur", null=True, blank=True)
    object_id = models.PositiveIntegerField(verbose_name="ID de l'auteur", null=True, blank=True)
    author = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    is_published = models.BooleanField(default=True, verbose_name="Publié")
    is_featured = models.BooleanField(default=False, verbose_name="À la une")
    
    # Ordre d'affichage
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name = "Actualité"
        verbose_name_plural = "Actualités"
    
    def __str__(self):
        return f"{self.title_fr} - {self.created_at.strftime('%d/%m/%Y')}"
    
    @property
    def has_media(self):
        """Vérifie si l'actualité a des médias attachés"""
        return bool(self.image or self.video)
    
    @property
    def media_type(self):
        """Retourne le type de média"""
        if self.image:
            return 'image'
        elif self.video:
            return 'video'
        return 'none'