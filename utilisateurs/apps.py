from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UtilisateursConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'utilisateurs'
    verbose_name = _('Utilisateurs')

    def ready(self):
        import utilisateurs.models  # Import signals
