from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Document, DocumentVersion

class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    readonly_fields = ('date_creation', 'taille_fichier')
    fields = ('numero_version', 'fichier', 'createur', 'commentaire', 'date_creation', 'taille_fichier')
    ordering = ['-numero_version']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'titre', 'type_document', 'statut', 'dossier', 'date_creation', 'version', 'taille_fichier_format')
    list_filter = ('type_document', 'statut', 'confidentiel', 'date_creation')
    search_fields = ('reference', 'titre', 'description', 'mots_cles', 'dossier__reference')
    date_hierarchy = 'date_creation'
    readonly_fields = ('reference', 'date_creation', 'date_modification', 'taille_fichier')
    inlines = [DocumentVersionInline]
    
    fieldsets = (
        (None, {
            'fields': (
                'reference',
                ('titre', 'type_document'),
                'dossier',
                'statut',
            )
        }),
        (_('Contenu'), {
            'fields': (
                'fichier',
                'description',
                'mots_cles',
            )
        }),
        (_('Métadonnées'), {
            'fields': (
                ('createur', 'validateur'),
                ('version', 'confidentiel'),
                'taille_fichier',
            )
        }),
        (_('Dates'), {
            'fields': (
                ('date_creation', 'date_modification'),
                'date_validation',
            ),
            'classes': ('collapse',)
        }),
    )

    def taille_fichier_format(self, obj):
        if obj.taille_fichier:
            # Convertir en KB/MB/GB selon la taille
            if obj.taille_fichier < 1024:
                return f"{obj.taille_fichier} B"
            elif obj.taille_fichier < 1024*1024:
                return f"{obj.taille_fichier/1024:.1f} KB"
            elif obj.taille_fichier < 1024*1024*1024:
                return f"{obj.taille_fichier/(1024*1024):.1f} MB"
            else:
                return f"{obj.taille_fichier/(1024*1024*1024):.1f} GB"
        return "-"
    taille_fichier_format.short_description = _('Taille')

    def save_model(self, request, obj, form, change):
        if not change:  # Si c'est une création
            obj.createur = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(dossier__avocat=request.user)
        return qs
