from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from clients.models import Client
from dossiers.models import Dossier

class Rendezvous(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = 'EA', _('En attente de validation')
        PLANIFIE = 'PL', _('Planifié')
        CONFIRME = 'CO', _('Confirmé')
        EN_COURS = 'EC', _('En cours')
        TERMINE = 'TE', _('Terminé')
        ANNULE = 'AN', _('Annulé')
        REFUSE = 'RE', _('Refusé')

    class Type(models.TextChoices):
        CONSULTATION = 'CO', _('Consultation')
        REUNION = 'RE', _('Réunion')
        AUDIENCE = 'AU', _('Audience')
        MEDIATION = 'ME', _('Médiation')
        AUTRE = 'AT', _('Autre')

    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='rendezvous',
        verbose_name=_('client')
    )
    avocat = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='rendezvous',
        verbose_name=_('avocat'),
        null=True,
        blank=True
    )
    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rendezvous',
        verbose_name=_('dossier associé')
    )
    type = models.CharField(
        max_length=2,
        choices=Type.choices,
        default=Type.CONSULTATION,
        verbose_name=_('type')
    )
    date_debut = models.DateTimeField(_('date de début'))
    date_fin = models.DateTimeField(_('date de fin'))
    lieu = models.CharField(_('lieu'), max_length=200, default='Cabinet')
    sujet = models.CharField(_('sujet'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    notes = models.TextField(_('notes internes'), blank=True)
    statut = models.CharField(
        max_length=2,
        choices=Statut.choices,
        default=Statut.EN_ATTENTE,
        verbose_name=_('statut')
    )
    motif_refus = models.TextField(_('motif de refus'), blank=True)
    date_proposition = models.DateTimeField(_('date proposée'), null=True, blank=True)
    rappel_envoye = models.BooleanField(_('rappel envoyé'), default=False)
    date_creation = models.DateTimeField(
        _('date de création'),
        default=timezone.now
    )
    date_modification = models.DateTimeField(
        _('date de modification'),
        default=timezone.now
    )

    class Meta:
        verbose_name = _('rendez-vous')
        verbose_name_plural = _('rendez-vous')
        ordering = ['date_debut']
        indexes = [
            models.Index(fields=['date_debut', 'date_fin']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.client} - {self.date_debut.strftime('%d/%m/%Y %H:%M')}"

    def clean(self):
        if self.date_debut and self.date_fin:
            if self.date_debut >= self.date_fin:
                raise ValidationError(_('La date de fin doit être postérieure à la date de début.'))
            
            # Only check for past dates when creating a new appointment or changing dates
            if not self.pk or (self._state.adding or 
                self.date_debut != Rendezvous.objects.get(pk=self.pk).date_debut):
                if self.date_debut < timezone.now() and self.statut in [self.Statut.PLANIFIE, self.Statut.EN_ATTENTE]:
                    raise ValidationError(_('Impossible de planifier un rendez-vous dans le passé.'))
        
        # Vérifier la disponibilité de l'avocat
        if self.avocat:
            conflits = Rendezvous.objects.filter(
                avocat=self.avocat,
                date_debut__lt=self.date_fin,
                date_fin__gt=self.date_debut,
                statut__in=[self.Statut.PLANIFIE, self.Statut.CONFIRME]
            ).exclude(pk=self.pk)
            
            if conflits.exists():
                raise ValidationError(_('L\'avocat a déjà un rendez-vous sur ce créneau.'))

    def save(self, *args, **kwargs):
        self.clean()
        
        if not self.pk:
            self.date_creation = timezone.now()
        self.date_modification = timezone.now()
        
        super().save(*args, **kwargs)

    @property
    def duree(self):
        if self.date_debut and self.date_fin:
            return self.date_fin - self.date_debut
        return None

    def est_en_retard(self):
        return self.date_debut < timezone.now() and self.statut == self.Statut.PLANIFIE
