from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden
from django.utils.translation import gettext_lazy as _
from functools import wraps
from django.shortcuts import get_object_or_404
from dossiers.models import Dossier
from documents.models import Document
from rendezvous.models import Rendezvous

def avocat_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_avocat:
            return HttpResponseForbidden(_("Vous devez être avocat pour accéder à cette page."))
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def secretaire_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_secretaire:
            return HttpResponseForbidden(_("Vous devez être secrétaire pour accéder à cette page."))
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def client_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_client:
            return HttpResponseForbidden(_("Vous devez être client pour accéder à cette page."))
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def check_dossier_access(user, dossier):
    """Vérifie si l'utilisateur peut accéder au dossier"""
    if not user or not dossier:
        return False
    if user.is_avocat:
        return True  # Les avocats peuvent voir tous les dossiers
    elif user.is_secretaire:
        return True
    elif user.is_client:
        return dossier.client.user == user
    return False

def check_document_access(user, document):
    """Vérifie si l'utilisateur peut accéder au document"""
    if not user or not document:
        return False
    if user.is_avocat:
        return True  # Les avocats peuvent voir tous les documents
    elif user.is_secretaire:
        return True
    elif user.is_client:
        return document.dossier.client.user == user and document.statut == 'VA'
    return False

def check_rendezvous_access(user, rendezvous):
    """Vérifie si l'utilisateur peut accéder au rendez-vous"""
    if not user or not rendezvous:
        return False
    if user.is_avocat:
        return True  # Les avocats peuvent voir tous les rendez-vous
    elif user.is_secretaire:
        return True
    elif user.is_client:
        return rendezvous.client.user == user
    return False

def can_view_dossier(view_func):
    @wraps(view_func)
    def _wrapped_view(request, reference, *args, **kwargs):
        dossier = get_object_or_404(Dossier, reference=reference)
        
        # Vérifier les permissions
        if request.user.is_avocat:
            if dossier.avocat != request.user:
                return HttpResponseForbidden(_("Vous n'avez pas accès à ce dossier."))
        elif request.user.is_secretaire:
            pass  # Les secrétaires peuvent voir tous les dossiers
        elif request.user.is_client:
            if dossier.client.user != request.user:
                return HttpResponseForbidden(_("Vous n'avez pas accès à ce dossier."))
        else:
            return HttpResponseForbidden(_("Vous n'avez pas accès à ce dossier."))
        
        kwargs['dossier'] = dossier
        return view_func(request, reference, *args, **kwargs)
    return _wrapped_view

def can_view_document(view_func):
    @wraps(view_func)
    def _wrapped_view(request, reference, *args, **kwargs):
        document = get_object_or_404(Document, reference=reference)
        
        # Vérifier les permissions
        if request.user.is_avocat:
            if document.dossier.avocat != request.user:
                return HttpResponseForbidden(_("Vous n'avez pas accès à ce document."))
        elif request.user.is_secretaire:
            pass  # Les secrétaires peuvent voir tous les documents
        elif request.user.is_client:
            if document.dossier.client.user != request.user:
                return HttpResponseForbidden(_("Vous n'avez pas accès à ce document."))
            if document.statut != 'VA':  # Les clients ne peuvent voir que les documents validés
                return HttpResponseForbidden(_("Ce document n'est pas encore validé."))
        else:
            return HttpResponseForbidden(_("Vous n'avez pas accès à ce document."))
        
        kwargs['document'] = document
        return view_func(request, reference, *args, **kwargs)
    return _wrapped_view

def can_view_rendezvous(function):
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        pk = kwargs.get('pk')
        if not pk:
            return HttpResponseForbidden(_("Identifiant du rendez-vous manquant."))
            
        try:
            rendezvous = get_object_or_404(Rendezvous, pk=pk)
            if check_rendezvous_access(request.user, rendezvous):
                kwargs['rendezvous'] = rendezvous
                return function(request, *args, **kwargs)
            return HttpResponseForbidden(_("Vous n'avez pas accès à ce rendez-vous."))
        except Rendezvous.DoesNotExist:
            return HttpResponseForbidden(_("Ce rendez-vous n'existe pas."))
    return wrapper 