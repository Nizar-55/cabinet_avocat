from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'type_client', 'civilite', 'nom', 'prenom',
            'email', 'telephone', 'telephone_secondaire',
            'adresse', 'code_postal', 'ville', 'pays',
            'date_naissance', 'lieu_naissance', 'nationalite', 'profession',
            'raison_sociale', 'numero_rc', 'ice',
            'notes'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'adresse': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Champs obligatoires de base
        self.fields['type_client'].required = True
        self.fields['civilite'].required = True
        self.fields['nom'].required = True
        self.fields['prenom'].required = True
        self.fields['email'].required = True
        
        # Initialiser les champs conditionnels
        if self.instance.pk:
            if self.instance.type_client != 'PAR':
                self.fields['raison_sociale'].required = True
                self.fields['numero_rc'].required = True
                self.fields['ice'].required = True
                self.fields['date_naissance'].required = False
                self.fields['nationalite'].required = False
            else:
                self.fields['date_naissance'].required = True
                self.fields['nationalite'].required = True
                self.fields['raison_sociale'].required = False
                self.fields['numero_rc'].required = False
                self.fields['ice'].required = False

    def clean(self):
        cleaned_data = super().clean()
        type_client = cleaned_data.get('type_client')

        # Validation de base
        required_fields = ['type_client', 'civilite', 'nom', 'prenom', 'email']
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, _('Ce champ est obligatoire.'))

        if type_client == 'PAR':
            # Validation pour les particuliers
            if not cleaned_data.get('date_naissance'):
                self.add_error('date_naissance', _('La date de naissance est requise pour les particuliers'))
            if not cleaned_data.get('nationalite'):
                self.add_error('nationalite', _('La nationalité est requise pour les particuliers'))
        else:
            # Validation pour les entreprises/associations
            if not cleaned_data.get('raison_sociale'):
                self.add_error('raison_sociale', _('La raison sociale est requise pour les entreprises/associations'))
            if not cleaned_data.get('numero_rc'):
                self.add_error('numero_rc', _('Le numéro RC est requis pour les entreprises/associations'))
            if not cleaned_data.get('ice'):
                self.add_error('ice', _('L\'ICE est requis pour les entreprises/associations'))

        return cleaned_data 