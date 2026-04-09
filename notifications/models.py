from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

class Notification(models.Model):
    class Type(models.TextChoices):
        RENDEZVOUS = 'RDV', _('Rendez-vous')
        DOCUMENT = 'DOC', _('Document')
        DOSSIER = 'DOS', _('Dossier')
        SYSTEME = 'SYS', _('Système')

    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('destinataire')
    )
    type = models.CharField(
        max_length=3,
        choices=Type.choices,
        default=Type.SYSTEME,
        verbose_name=_('type')
    )
    titre = models.CharField(_('titre'), max_length=200)
    message = models.TextField(_('message'))
    date_creation = models.DateTimeField(_('date de création'), auto_now_add=True)
    date_lecture = models.DateTimeField(_('date de lecture'), null=True, blank=True)
    
    # Generic relation to the related object
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-date_creation']
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        indexes = [
            models.Index(fields=['destinataire', 'date_creation']),
            models.Index(fields=['type']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.titre}"

    def marquer_comme_lue(self):
        from django.utils import timezone
        self.date_lecture = timezone.now()
        self.save()
        
    def get_related_object(self):
        """Get the related object safely"""
        try:
            if self.content_type and self.object_id:
                return self.content_object
        except ObjectDoesNotExist:
            return None
        return None
