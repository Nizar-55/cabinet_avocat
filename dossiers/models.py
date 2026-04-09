from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import transaction
from clients.models import Client
from django.conf import settings

class Dossier(models.Model):
    class Statut(models.TextChoices):
        EN_COURS = 'EC', _('En cours')
        EN_ATTENTE = 'EA', _('En attente')
        TERMINE = 'TE', _('Terminé')
        ARCHIVE = 'AR', _('Archivé')

    reference = models.CharField(
        max_length=20,
        unique=True,
        help_text=_('Référence unique du dossier'),
        verbose_name=_('référence'),
        default='DOS000000'
    )
    titre = models.CharField(_('titre'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='dossiers',
        verbose_name=_('client')
    )
    avocat = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='dossiers_avocat',
        verbose_name=_('avocat')
    )
    statut = models.CharField(
        max_length=2,
        choices=Statut.choices,
        default=Statut.EN_COURS,
        verbose_name=_('statut')
    )
    date_creation = models.DateTimeField(
        _('date de création'),
        default=timezone.now
    )
    date_modification = models.DateTimeField(
        _('date de modification'),
        default=timezone.now
    )
    date_cloture = models.DateTimeField(
        _('date de clôture'),
        null=True,
        blank=True
    )
    
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_('Notes internes sur le dossier')
    )
    montant_facture = models.DecimalField(
        _('montant facturé'),
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text=_('Montant total facturé pour ce dossier')
    )

    class Meta:
        verbose_name = _('dossier')
        verbose_name_plural = _('dossiers')
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['reference']),
            models.Index(fields=['statut']),
            models.Index(fields=['client']),
            models.Index(fields=['avocat']),
        ]

    def __str__(self):
        return f"{self.reference} - {self.titre}"

    def save(self, *args, **kwargs):
        if not self.reference or self.reference == 'DOS000000':
            with transaction.atomic():
                last_dossier = Dossier.objects.order_by('-id').select_for_update().first()
                last_id = last_dossier.id if last_dossier else 0
                self.reference = f'DOS{str(last_id + 1).zfill(6)}'
        
        if not self.pk:
            self.date_creation = timezone.now()
        self.date_modification = timezone.now()
        
        if self.statut in [self.Statut.TERMINE, self.Statut.ARCHIVE] and not self.date_cloture:
            self.date_cloture = timezone.now()
        
        super().save(*args, **kwargs)