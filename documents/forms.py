from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Document, DocumentVersion

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            'titre', 'type_document', 'fichier', 'dossier',
            'description', 'mots_cles', 'confidentiel'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'mots_cles': forms.TextInput(attrs={'placeholder': _('Séparez les mots-clés par des virgules')}),
        }

class DocumentVersionForm(forms.ModelForm):
    class Meta:
        model = DocumentVersion
        fields = ['fichier', 'commentaire']
        widgets = {
            'commentaire': forms.Textarea(attrs={'rows': 3}),
        } 