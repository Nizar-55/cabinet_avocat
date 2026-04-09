from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from .models import Utilisateur
from clients.models import Client

class ClientInscriptionForm(UserCreationForm):
    """Formulaire d'inscription pour les clients uniquement"""
    class Meta(UserCreationForm.Meta):
        model = Utilisateur
        fields = ['username', 'email', 'first_name', 'last_name']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError(_('L\'adresse email est obligatoire.'))
        
        # Vérifier si l'email existe déjà dans la table Client
        try:
            client = Client.objects.get(email=email)
            if client.user is not None:
                raise forms.ValidationError(_('Un compte avec cette adresse email existe déjà.'))
        except Client.DoesNotExist:
            pass
            
        return email
        
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name:
            raise forms.ValidationError(_('Le prénom est obligatoire.'))
        return first_name
        
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name:
            raise forms.ValidationError(_('Le nom est obligatoire.'))
        return last_name
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'client'  # Force le rôle client
        
        if commit:
            user.save()
            # Vérifier si un profil client existe déjà avec cet email
            try:
                client = Client.objects.get(email=user.email)
                # Si le client existe mais n'a pas d'utilisateur associé, on le lie
                if client.user is None:
                    client.user = user
                    client.nom = user.last_name
                    client.prenom = user.first_name
                    client.save()
            except Client.DoesNotExist:
                # Créer un nouveau profil client si aucun n'existe
                Client.objects.create(
                    user=user,
                    nom=user.last_name,
                    prenom=user.first_name,
                    email=user.email,
                    type_client='PAR',
                    civilite='M'
                )
        return user

class AdminUtilisateurCreationForm(UserCreationForm):
    """Formulaire pour la création d'utilisateurs par l'admin (avocats et secrétaires uniquement)"""
    role = forms.ChoiceField(
        choices=[('avocat', _('Avocat')), ('secretaire', _('Secrétaire'))],
        label=_('Rôle'),
        widget=forms.RadioSelect,
        help_text=_('Sélectionnez le rôle de l\'utilisateur')
    )
    
    class Meta(UserCreationForm.Meta):
        model = Utilisateur
        fields = ['username', 'email', 'first_name', 'last_name', 'role']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError(_('L\'adresse email est obligatoire.'))
        return email
        
    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        user.role = role
        
        if commit:
            user.save()
            if role in ['avocat', 'secretaire']:
                user.is_staff = True
                user.save()
        return user

class UtilisateurProfileForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['first_name', 'last_name', 'email', 'telephone', 'telephone_mobile', 
                 'photo', 'date_naissance', 'adresse', 'ville', 'code_postal', 'pays']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }

class AvocatProfileForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = [
            'photo', 'telephone', 'telephone_mobile', 'date_naissance',
            'adresse', 'ville', 'code_postal', 'pays',
            'specialite', 'barreau', 'numero_avocat', 'date_prestation_serment'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
            'date_prestation_serment': forms.DateInput(attrs={'type': 'date'}),
        }

class SecretaireProfileForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = [
            'photo', 'telephone', 'telephone_mobile', 'date_naissance',
            'adresse', 'ville', 'code_postal', 'pays',
            'departement', 'poste'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }

class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = [
            'photo', 'telephone', 'telephone_mobile', 'date_naissance',
            'adresse', 'ville', 'code_postal', 'pays'
        ]
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'}) 