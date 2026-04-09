from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Dossier

class DossierForm(forms.ModelForm):
    class Meta:
        model = Dossier
        fields = [
            'titre', 'description', 'client', 'statut',
            'notes', 'montant_facture'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        } 