from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseForbidden
from .models import Dossier
from .forms import DossierForm
from utilisateurs.decorators import can_view_dossier, avocat_required

@login_required
def dossier_list(request):
    if request.user.is_avocat:
        dossiers = Dossier.objects.all()  # Les avocats peuvent voir tous les dossiers
    elif request.user.is_secretaire:
        dossiers = Dossier.objects.all()
    elif request.user.is_client:
        dossiers = Dossier.objects.filter(client__user=request.user)
    else:
        return HttpResponseForbidden(_("Vous n'avez pas accès à cette page."))
        
    dossiers = dossiers.order_by('-date_creation')
    return render(request, 'dossiers/dossier_list.html', {'dossiers': dossiers})

@login_required
@avocat_required
def dossier_create(request):
    if request.method == 'POST':
        form = DossierForm(request.POST)
        if form.is_valid():
            dossier = form.save(commit=False)
            dossier.avocat = request.user
            dossier.save()
            messages.success(request, _('Le dossier a été créé avec succès.'))
            return redirect('dossiers:detail', reference=dossier.reference)
    else:
        form = DossierForm()
    
    return render(request, 'dossiers/dossier_form.html', {
        'form': form,
        'title': _('Nouveau dossier')
    })

@login_required
def dossier_detail(request, reference):
    dossier = get_object_or_404(Dossier, reference=reference)
    
    # Vérification des permissions
    if not can_view_dossier(request.user, dossier):
        return HttpResponseForbidden(_("Vous n'avez pas la permission de voir ce dossier."))
        
    return render(request, 'dossiers/dossier_detail.html', {'dossier': dossier})

@login_required
def dossier_update(request, reference):
    dossier = get_object_or_404(Dossier, reference=reference)
    
    # Vérification des permissions
    if not can_view_dossier(request.user, dossier):
        return HttpResponseForbidden(_("Vous n'avez pas la permission de voir ce dossier."))
    
    if not (request.user.is_avocat and dossier.avocat == request.user):
        return HttpResponseForbidden(_("Vous n'avez pas la permission de modifier ce dossier."))
    
    if request.method == 'POST':
        form = DossierForm(request.POST, instance=dossier)
        if form.is_valid():
            dossier = form.save()
            messages.success(request, _('Le dossier a été modifié avec succès.'))
            return redirect('dossiers:detail', reference=dossier.reference)
    else:
        form = DossierForm(instance=dossier)
    
    return render(request, 'dossiers/dossier_form.html', {
        'form': form,
        'dossier': dossier,
        'title': _('Modifier le dossier')
    })

@login_required
@avocat_required
def dossier_delete(request, reference):
    dossier = get_object_or_404(Dossier, reference=reference, avocat=request.user)
    if request.method == 'POST':
        dossier.delete()
        messages.success(request, _('Le dossier a été supprimé avec succès.'))
        return redirect('dossiers:list')
    
    return render(request, 'dossiers/dossier_confirm_delete.html', {'dossier': dossier})

def can_view_dossier(user, dossier):
    """Vérifie si l'utilisateur peut voir le dossier"""
    if user.is_avocat:
        return True  # Les avocats peuvent voir tous les dossiers
    elif user.is_secretaire:
        return True  # La secrétaire peut voir tous les dossiers
    elif user.is_client:
        return dossier.client.user == user
    return False
