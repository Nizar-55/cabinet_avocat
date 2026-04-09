from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.db import transaction
from dossiers.models import Dossier

class Document(models.Model):
    class Type(models.TextChoices):
        CONTRAT = 'CO', _('Contrat')
        JUGEMENT = 'JU', _('Jugement')
        REQUETE = 'RE', _('Requête')
        MEMOIRE = 'ME', _('Mémoire')
        PIECE = 'PI', _('Pièce')
        CORRESPONDANCE = 'CR', _('Correspondance')
        FACTURE = 'FA', _('Facture')
        AUTRE = 'AU', _('Autre')

    class Statut(models.TextChoices):
        BROUILLON = 'BR', _('Brouillon')
        EN_REVISION = 'RE', _('En révision')
        VALIDE = 'VA', _('Validé')
        ARCHIVE = 'AR', _('Archivé')

    titre = models.CharField(_('titre'), max_length=200)
    reference = models.CharField(_('référence'), max_length=50, unique=True)
    type_document = models.CharField(
        _('type de document'),
        max_length=2,
        choices=Type.choices,
        default=Type.AUTRE
    )
    statut = models.CharField(
        _('statut'),
        max_length=2,
        choices=Statut.choices,
        default=Statut.BROUILLON
    )
    fichier = models.FileField(
        _('fichier'),
        upload_to='documents/%Y/%m/',
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'odt', 'txt']
        )]
    )
    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.PROTECT,
        related_name='documents',
        verbose_name=_('dossier')
    )
    date_creation = models.DateTimeField(
        _('date de création'),
        default=timezone.now
    )
    date_modification = models.DateTimeField(
        _('date de modification'),
        default=timezone.now
    )
    date_validation = models.DateTimeField(
        _('date de validation'),
        null=True,
        blank=True
    )
    createur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='documents_crees',
        verbose_name=_('créateur')
    )
    validateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents_valides',
        verbose_name=_('validateur')
    )
    description = models.TextField(_('description'), blank=True)
    mots_cles = models.CharField(_('mots-clés'), max_length=200, blank=True)
    version = models.PositiveIntegerField(_('version'), default=1)
    confidentiel = models.BooleanField(_('confidentiel'), default=False)
    taille_fichier = models.PositiveIntegerField(_('taille du fichier'), editable=False, null=True)

    class Meta:
        ordering = ['-date_modification']
        verbose_name = _('document')
        verbose_name_plural = _('documents')
        indexes = [
            models.Index(fields=['reference']),
            models.Index(fields=['type_document', 'statut']),
            models.Index(fields=['date_creation']),
        ]

    def __str__(self):
        return f"{self.reference} - {self.titre} (v{self.version})"

    def save(self, *args, **kwargs):
        if not self.reference:
            with transaction.atomic():
                prefix = self.Type(self.type_document).label[:2].upper()
                last_doc = Document.objects.filter(type_document=self.type_document).order_by('-id').select_for_update().first()
                last_num = int(last_doc.reference.split('-')[-1]) if last_doc else 0
                self.reference = f"{prefix}-{str(last_num + 1).zfill(6)}"
        
        if self.fichier:
            self.taille_fichier = self.fichier.size
        
        if not self.pk:
            self.date_creation = timezone.now()
        self.date_modification = timezone.now()
        
        super().save(*args, **kwargs)

class DocumentVersion(models.Model):
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name=_('document')
    )
    fichier = models.FileField(
        _('fichier'),
        upload_to='documents/versions/%Y/%m/',
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'doc', 'docx', 'odt', 'txt']
        )]
    )
    numero_version = models.PositiveIntegerField(_('numéro de version'))
    date_creation = models.DateTimeField(
        _('date de création'),
        default=timezone.now
    )
    createur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_('créateur')
    )
    commentaire = models.TextField(_('commentaire'), blank=True)
    taille_fichier = models.PositiveIntegerField(_('taille du fichier'), editable=False, null=True)

    class Meta:
        ordering = ['-numero_version']
        unique_together = ['document', 'numero_version']
        verbose_name = _('version du document')
        verbose_name_plural = _('versions du document')
        indexes = [
            models.Index(fields=['document', 'numero_version']),
        ]

    def __str__(self):
        return f"{self.document.reference} - v{self.numero_version}"

    def save(self, *args, **kwargs):
        if self.fichier:
            self.taille_fichier = self.fichier.size
        
        if not self.pk:
            self.date_creation = timezone.now()
            # Auto-increment version number
            if not self.numero_version:
                last_version = self.document.versions.order_by('-numero_version').first()
                self.numero_version = (last_version.numero_version + 1) if last_version else 1
        
        super().save(*args, **kwargs)