from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import Rendezvous

class RendezvousForm(forms.ModelForm):
    class Meta:
        model = Rendezvous
        fields = [
            'client', 'avocat', 'dossier', 'type', 'date_debut', 'date_fin',
            'lieu', 'sujet', 'description', 'notes'
        ]
        widgets = {
            'date_debut': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'date_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')

        if date_debut and date_fin:
            if date_fin <= date_debut:
                raise forms.ValidationError(
                    _('La date de fin doit être postérieure à la date de début.')
                )

        return cleaned_data

class RendezvousRequestForm(forms.ModelForm):
    """Form for clients to request appointments"""
    date_souhaitee = forms.DateField(
        label=_('Date souhaitée'),
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text=_('Choisissez la date qui vous convient le mieux')
    )
    
    heure_souhaitee = forms.ChoiceField(
        label=_('Heure souhaitée'),
        choices=[
            ('09:00', '09:00'),
            ('10:00', '10:00'),
            ('11:00', '11:00'),
            ('14:00', '14:00'),
            ('15:00', '15:00'),
            ('16:00', '16:00'),
        ],
        help_text=_('Choisissez l\'heure qui vous convient le mieux')
    )

    class Meta:
        model = Rendezvous
        fields = ['type', 'sujet', 'description']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': _('Décrivez brièvement l\'objet de votre rendez-vous')
            }),
            'sujet': forms.TextInput(attrs={
                'placeholder': _('Ex: Consultation initiale, Question juridique, etc.')
            })
        }

    def clean_date_souhaitee(self):
        date = self.cleaned_data['date_souhaitee']
        if date < timezone.now().date():
            raise forms.ValidationError(_('La date ne peut pas être dans le passé.'))
        return date

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Combine date and time
        date = self.cleaned_data['date_souhaitee']
        heure = self.cleaned_data['heure_souhaitee']
        date_debut = timezone.datetime.combine(
            date,
            timezone.datetime.strptime(heure, '%H:%M').time(),
            tzinfo=timezone.get_current_timezone()
        )
        
        # Set appointment duration to 1 hour by default
        instance.date_debut = date_debut
        instance.date_fin = date_debut + timezone.timedelta(hours=1)
        instance.statut = Rendezvous.Statut.EN_ATTENTE
        
        if commit:
            instance.save()
        return instance

class RendezvousRefuseForm(forms.ModelForm):
    """Form for refusing appointments"""
    class Meta:
        model = Rendezvous
        fields = ['motif_refus']
        widgets = {
            'motif_refus': forms.Textarea(attrs={'rows': 3}),
        }

class RendezvousDatePropositionForm(forms.ModelForm):
    """Form for proposing new dates"""
    class Meta:
        model = Rendezvous
        fields = ['date_proposition']
        widgets = {
            'date_proposition': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_proposition = cleaned_data.get('date_proposition')
        
        if date_proposition and date_proposition < timezone.now():
            raise forms.ValidationError(_('La date proposée ne peut pas être dans le passé.'))
        
        return cleaned_data 