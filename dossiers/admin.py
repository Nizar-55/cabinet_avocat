from django.contrib import admin
from .models import Dossier

@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = ('reference', 'client', 'statut', 'date_creation')
    list_filter = ('statut', 'date_creation')
    search_fields = ('reference', 'client__nom', 'client__prenom')
    date_hierarchy = 'date_creation'
    ordering = ('-date_creation',)
