from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .forms import (ClientInscriptionForm, AdminUtilisateurCreationForm, AvocatProfileForm, 
                   SecretaireProfileForm, ClientProfileForm, CustomPasswordChangeForm, UtilisateurProfileForm)
from .models import Utilisateur
import logging

logger = logging.getLogger(__name__)

def is_admin_or_avocat(user):
    return user.is_superuser or user.role == 'avocat'

def register_client(request):
    """Vue pour l'inscription des clients"""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = ClientInscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('Votre compte a été créé avec succès.'))
            return redirect('home')
    else:
        form = ClientInscriptionForm()
    
    return render(request, 'utilisateurs/register.html', {
        'form': form,
        'title': _('Inscription')
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, _('Connexion réussie.'))
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'utilisateurs/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, _('Déconnexion réussie.'))
    return redirect('home')

@login_required
def profile_view(request):
    if request.method == 'POST':
        if request.user.role == 'avocat':
            form = AvocatProfileForm(request.POST, request.FILES, instance=request.user)
        elif request.user.role == 'secretaire':
            form = SecretaireProfileForm(request.POST, request.FILES, instance=request.user)
        else:
            form = ClientProfileForm(request.POST, request.FILES, instance=request.user)
            
        if form.is_valid():
            form.save()
            messages.success(request, _('Votre profil a été mis à jour avec succès.'))
            return redirect('utilisateurs:profile')
    else:
        if request.user.role == 'avocat':
            form = AvocatProfileForm(instance=request.user)
        elif request.user.role == 'secretaire':
            form = SecretaireProfileForm(instance=request.user)
        else:
            form = ClientProfileForm(instance=request.user)
    
    return render(request, 'utilisateurs/profile.html', {
        'form': form,
        'user': request.user
    })

@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _('Votre mot de passe a été modifié avec succès.'))
            return redirect('utilisateurs:profile')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    
    return render(request, 'utilisateurs/password_change.html', {'form': form})

@login_required
def utilisateur_detail(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    return render(request, 'utilisateurs/utilisateur_detail.html', {
        'utilisateur': utilisateur,
        'title': _('Détails du profil')
    })

@login_required
@user_passes_test(is_admin_or_avocat)
def utilisateur_update(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    if utilisateur.role == 'avocat':
        form_class = AvocatProfileForm
    else:
        form_class = SecretaireProfileForm
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=utilisateur)
        if form.is_valid():
            form.save()
            messages.success(request, _('Le profil a été modifié avec succès.'))
            return redirect('utilisateurs:detail', pk=utilisateur.pk)
    else:
        form = form_class(instance=utilisateur)
    
    return render(request, 'utilisateurs/create_profile.html', {
        'form': form,
        'title': _('Modifier le profil'),
        'utilisateur': utilisateur
    })

@login_required
@user_passes_test(is_admin_or_avocat)
def create_utilisateur(request):
    """Vue pour la création d'utilisateurs par l'admin (avocats et secrétaires uniquement)"""
    if request.method == 'POST':
        form = AdminUtilisateurCreationForm(request.POST)
        try:
            if form.is_valid():
                utilisateur = form.save()
                messages.success(request, _('Le compte utilisateur a été créé avec succès.'))
                
                # Rediriger vers le formulaire de profil approprié
                if utilisateur.role == 'avocat':
                    return redirect('utilisateurs:create_avocat_profile', pk=utilisateur.pk)
                elif utilisateur.role == 'secretaire':
                    return redirect('utilisateurs:create_secretaire_profile', pk=utilisateur.pk)
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        except Exception as e:
            messages.error(request, _('Une erreur est survenue lors de la création du compte.'))
            logger.error(f"Erreur lors de la création de l'utilisateur: {str(e)}")
    else:
        form = AdminUtilisateurCreationForm()
    
    return render(request, 'utilisateurs/create_utilisateur.html', {
        'form': form,
        'title': _('Créer un nouveau compte personnel')
    })

@login_required
@user_passes_test(is_admin_or_avocat)
def create_avocat_profile(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    if request.method == 'POST':
        form = AvocatProfileForm(request.POST, request.FILES, instance=utilisateur)
        if form.is_valid():
            form.save()
            messages.success(request, _('Le profil avocat a été créé avec succès.'))
            return redirect('utilisateurs:detail', pk=utilisateur.pk)
    else:
        form = AvocatProfileForm(instance=utilisateur)
    
    return render(request, 'utilisateurs/create_profile.html', {
        'form': form,
        'title': _('Compléter le profil avocat'),
        'utilisateur': utilisateur
    })

@login_required
@user_passes_test(is_admin_or_avocat)
def create_secretaire_profile(request, pk):
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    if request.method == 'POST':
        form = SecretaireProfileForm(request.POST, request.FILES, instance=utilisateur)
        if form.is_valid():
            form.save()
            messages.success(request, _('Le profil secrétaire a été créé avec succès.'))
            return redirect('utilisateurs:detail', pk=utilisateur.pk)
    else:
        form = SecretaireProfileForm(instance=utilisateur)
    
    return render(request, 'utilisateurs/create_profile.html', {
        'form': form,
        'title': _('Compléter le profil secrétaire'),
        'utilisateur': utilisateur
    })
