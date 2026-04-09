from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('avocat', _('Avocat')),
        ('secretaire', _('Secrétaire')),
        ('client', _('Client')),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name=_('rôle')
    )
    telephone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name=_('téléphone')
    )
    telephone_mobile = models.CharField(
        max_length=15,
        blank=True,
        verbose_name=_('téléphone mobile')
    )
    photo = models.ImageField(
        upload_to='utilisateurs/photos/',
        blank=True,
        null=True,
        verbose_name=_('photo')
    )
    date_naissance = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('date de naissance')
    )
    adresse = models.TextField(
        blank=True,
        verbose_name=_('adresse')
    )
    ville = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('ville')
    )
    code_postal = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_('code postal')
    )
    pays = models.CharField(
        max_length=100,
        default='Maroc',
        verbose_name=_('pays')
    )
    
    # Champs spécifiques pour les avocats
    specialite = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('spécialité')
    )
    barreau = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('barreau')
    )
    numero_avocat = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('numéro d\'avocat')
    )
    date_prestation_serment = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('date de prestation de serment')
    )
    
    # Champs spécifiques pour les secrétaires
    departement = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('département')
    )
    poste = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('poste')
    )
    
    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.get_role_display()}"
    
    def get_profile_completion(self):
        """Calcule le pourcentage de complétion du profil"""
        fields = ['first_name', 'last_name', 'email', 'telephone', 'adresse', 'ville']
        if self.role == 'avocat':
            fields.extend(['specialite', 'barreau', 'numero_avocat'])
        elif self.role == 'secretaire':
            fields.extend(['departement', 'poste'])
            
        filled = sum(1 for field in fields if getattr(self, field))
        return (filled / len(fields)) * 100
        
    @property
    def is_avocat(self):
        """Check if the user is a lawyer"""
        return self.role == 'avocat'
        
    @property
    def is_secretaire(self):
        """Check if the user is a secretary"""
        return self.role == 'secretaire'
        
    @property
    def is_staff_member(self):
        """Check if the user is a staff member (lawyer or secretary)"""
        return self.is_avocat or self.is_secretaire
        
    def has_client_access(self):
        """Check if the user has access to client information"""
        return self.is_staff_member
        
    def has_dossier_access(self):
        """Check if the user has access to case files"""
        return self.is_staff_member
        
    def has_admin_access(self):
        """Check if the user has administrative access"""
        return self.is_avocat or self.is_superuser

    @property
    def is_client(self):
        """Check if the user is a client"""
        return self.role == 'client'

class LawCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('nom'))
    description = models.TextField(verbose_name=_('description'))
    icon = models.ImageField(
        upload_to='law_categories/',
        verbose_name=_('icône'),
        help_text=_('Une image représentative pour cette catégorie de droit')
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_('ordre'),
        help_text=_('Ordre d\'affichage')
    )

    class Meta:
        verbose_name = _('catégorie de droit')
        verbose_name_plural = _('catégories de droit')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

@receiver(post_save, sender=Utilisateur)
def create_client_profile(sender, instance, created, **kwargs):
    """Create a client profile when a user with role 'client' is created"""
    if created and instance.role == 'client':
        from clients.models import Client
        if not hasattr(instance, 'client') or instance.client is None:
            Client.objects.create(
                user=instance,
                nom=instance.last_name,
                prenom=instance.first_name,
                email=instance.email,
                type_client='PAR',
                civilite='M'
            )
