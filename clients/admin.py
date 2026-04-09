from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'telephone', 'ville', 'date_creation')
    list_filter = ('date_creation', 'ville', 'pays')
    search_fields = ('nom', 'prenom', 'email', 'telephone', 'adresse', 'ville')
    date_hierarchy = 'date_creation'
    readonly_fields = ('date_creation', 'date_modification')
    fieldsets = (
        (_('Informations personnelles'), {
            'fields': (('civilite', 'nom', 'prenom'), 'email')
        }),
        (_('Coordonnées'), {
            'fields': (('telephone', 'telephone_secondaire'),
                      'adresse',
                      ('code_postal', 'ville'),
                      'pays')
        }),
        (_('Informations complémentaires'), {
            'fields': ('notes',)
        }),
        (_('Dates'), {
            'fields': (('date_creation', 'date_modification'),),
            'classes': ('collapse',)
        }),
    )
