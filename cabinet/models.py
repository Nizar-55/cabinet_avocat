from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class ActivityLog(models.Model):
    ACTIONS = [
        ('CREATE', 'Création'),
        ('UPDATE', 'Modification'),
        ('DELETE', 'Suppression'),
        ('LOGIN', 'Connexion'),
        ('LOGOUT', 'Déconnexion'),
        ('OTHER', 'Autre'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=20, choices=ACTIONS)
    description = models.TextField()
    target_model = models.CharField(max_length=50)
    target_id = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Journal d\'activité'
        verbose_name_plural = 'Journal d\'activités'

    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.timestamp}"


class SystemAlert(models.Model):
    LEVELS = [
        ('INFO', 'Information'),
        ('WARNING', 'Avertissement'),
        ('ERROR', 'Erreur'),
        ('CRITICAL', 'Critique'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    level = models.CharField(max_length=10, choices=LEVELS, default='INFO')
    timestamp = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    source = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Alerte système'
        verbose_name_plural = 'Alertes système'

    def __str__(self):
        return f"{self.get_level_display()} - {self.title}"

    def resolve(self, user):
        self.resolved = True
        self.resolved_by = user
        self.resolved_at = timezone.now()
        self.save()

    @classmethod
    def create_info(cls, title, message, source=None):
        return cls.objects.create(
            title=title,
            message=message,
            level='INFO',
            source=source
        )

    @classmethod
    def create_warning(cls, title, message, source=None):
        return cls.objects.create(
            title=title,
            message=message,
            level='WARNING',
            source=source
        )

    @classmethod
    def create_error(cls, title, message, source=None):
        return cls.objects.create(
            title=title,
            message=message,
            level='ERROR',
            source=source
        )

    @classmethod
    def create_critical(cls, title, message, source=None):
        return cls.objects.create(
            title=title,
            message=message,
            level='CRITICAL',
            source=source
        ) 