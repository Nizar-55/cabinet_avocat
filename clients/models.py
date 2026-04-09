from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils import timezone
from django.conf import settings

class Client(models.Model):
    class Civilite(models.TextChoices):
        MONSIEUR = 'M', _('Monsieur')
        MADAME = 'MME', _('Madame')
        AUTRE = 'AUTRE', _('Autre')

    class TypeClient(models.TextChoices):
        PARTICULIER = 'PAR', _('Particulier')
        ENTREPRISE = 'ENT', _('Entreprise')
        ASSOCIATION = 'ASS', _('Association')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='client',
        verbose_name=_('utilisateur')
    )

    civilite = models.CharField(
        max_length=5,
        choices=Civilite.choices,
        default=Civilite.MONSIEUR,
        verbose_name=_('civilité')
    )
    type_client = models.CharField(
        max_length=3,
        choices=TypeClient.choices,
        default=TypeClient.PARTICULIER,
        verbose_name=_('type de client')
    )
    nom = models.CharField(_('nom'), max_length=50) 
    prenom = models.CharField(_('prénom'), max_length=50)
    
    email = models.EmailField(_('email'), max_length=50, unique=True)
    telephone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_('Le numéro de téléphone doit être au format: "+999999999". Maximum 15 chiffres autorisés.')
    )
    telephone = models.CharField(
        _('téléphone'),
        validators=[telephone_regex],
        max_length=20,
        blank=True
    )
    telephone_secondaire = models.CharField(
        _('téléphone secondaire'),
        validators=[telephone_regex],
        max_length=20,
        blank=True
    )
    
    adresse = models.TextField(_('adresse'), blank=True)
    code_postal = models.CharField(
        _('code postal'),
        max_length=10,
        blank=True
    )
    ville = models.CharField(
        _('ville'),
        max_length=100,
        blank=True
    )
    pays = models.CharField(
        _('pays'),
        max_length=100,
        default='Maroc'
    )
    
    date_naissance = models.DateField(
        _('date de naissance'),
        null=True,
        blank=True
    )
    lieu_naissance = models.CharField(
        _('lieu de naissance'),
        max_length=100,
        blank=True
    )
    nationalite = models.CharField(
        _('nationalité'),
        max_length=100,
        default='Marocaine'
    )
    profession = models.CharField(
        _('profession'),
        max_length=100,
        blank=True
    )
    
    raison_sociale = models.CharField(
        _('raison sociale'),
        max_length=200,
        blank=True
    )
    numero_rc = models.CharField(
        _('numéro RC'),
        max_length=50,
        blank=True,
        validators=[MinLengthValidator(5)]
    )
    ice = models.CharField(
        _('ICE'),
        max_length=50,
        blank=True,
        validators=[MinLengthValidator(15)]
    )
    
    date_creation = models.DateTimeField(
        _('date de création'),
        default=timezone.now
    )
    date_modification = models.DateTimeField(
        _('date de modification'),
        default=timezone.now
    )
    notes = models.TextField(_('notes'), blank=True)
    class Meta:
        verbose_name = _('client')
        verbose_name_plural = _('clients')
        ordering = ['nom', 'prenom']
        indexes = [
            models.Index(fields=['nom'], name='client_nom_idx'),
            models.Index(fields=['prenom'], name='client_prenom_idx'),
            models.Index(fields=['email'], name='client_email_idx'),
            models.Index(fields=['type_client'], name='client_type_idx')
        ]
    def __str__(self):
        if self.type_client == self.TypeClient.PARTICULIER:
            return f"{self.get_civilite_display()} {self.nom} {self.prenom}"
        else:
            return self.raison_sociale or f"{self.nom} {self.prenom}"

    def get_full_address(self):
        address_parts = [part for part in [self.adresse, self.code_postal, self.ville, self.pays] if part]
        return "\n".join(address_parts) if address_parts else ""

    def save(self, *args, **kwargs):
        if not self.pk:
            self.date_creation = timezone.now()
        self.date_modification = timezone.now()
        super().save(*args, **kwargs)

    def get_profile_completion(self):
        fields = ['nom', 'prenom', 'email', 'telephone', 'adresse', 'ville', 'code_postal']
        
        if self.type_client == self.TypeClient.PARTICULIER:
            fields.extend(['date_naissance', 'lieu_naissance', 'nationalite', 'profession'])
        else:
            fields.extend(['raison_sociale', 'numero_rc', 'ice'])
            
        filled = sum(1 for field in fields if getattr(self, field))
        return (filled / len(fields)) * 100