from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Rendezvous

@admin.register(Rendezvous)
class RendezvousAdmin(admin.ModelAdmin):
    list_display = ('client', 'avocat', 'type', 'date_debut', 'date_fin', 'lieu', 'statut')
    list_filter = ('statut', 'type', 'avocat', 'lieu')
    search_fields = ('client__nom', 'client__prenom', 'avocat__username', 'sujet', 'description')
    date_hierarchy = 'date_debut'
    readonly_fields = ('date_creation', 'date_modification', 'rappel_envoye')
    
    fieldsets = (
        (None, {
            'fields': (
                ('type', 'statut'),
                ('client', 'avocat'),
                'dossier',
            )
        }),
        (_('Détails du rendez-vous'), {
            'fields': (
                ('date_debut', 'date_fin'),
                'lieu',
                'sujet',
                'description',
                'notes',
            )
        }),
        (_('Informations système'), {
            'fields': (
                ('date_creation', 'date_modification'),
                'rappel_envoye'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(avocat=request.user)
        return qs
