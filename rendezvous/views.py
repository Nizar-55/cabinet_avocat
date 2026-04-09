from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import Rendezvous
from .forms import RendezvousForm, RendezvousRequestForm, RendezvousRefuseForm, RendezvousDatePropositionForm
from utilisateurs.models import Utilisateur
from notifications.utils import notifier_rendezvous
from utilisateurs.decorators import can_view_rendezvous, avocat_required, secretaire_required

@login_required
def rendezvous_list(request):
    if request.user.is_avocat:
        # Les avocats peuvent voir tous les rendez-vous
        rendezvous = Rendezvous.objects.all()
    elif request.user.is_secretaire:
        # Les secrétaires peuvent voir tous les rendez-vous
        rendezvous = Rendezvous.objects.all()
    elif request.user.is_client:
        # Les clients ne voient que leurs rendez-vous
        rendezvous = Rendezvous.objects.filter(client__user=request.user)
    else:
        return HttpResponseForbidden(_("Vous n'avez pas accès à cette page."))
        
    rendezvous = rendezvous.order_by('-date_debut')
    return render(request, 'rendezvous/rendezvous_list.html', {'rendezvous': rendezvous})

@login_required
def rendezvous_create(request):
    """Vue pour créer un rendez-vous (avocats et secrétaires)"""
    if not (request.user.is_avocat or request.user.is_secretaire):
        return HttpResponseForbidden(_("Vous n'avez pas la permission de créer des rendez-vous."))

    if request.method == 'POST':
        form = RendezvousForm(request.POST)
        if form.is_valid():
            rendezvous = form.save(commit=False)
            if request.user.is_avocat:
                rendezvous.avocat = request.user
            rendezvous.save()
            notifier_rendezvous(rendezvous, 'create')
            messages.success(request, _('Le rendez-vous a été créé avec succès.'))
            return redirect('rendezvous:detail', pk=rendezvous.pk)
    else:
        initial = {}
        form = RendezvousForm(initial=initial)
        if request.user.is_avocat:
            form.fields['avocat'].initial = request.user
            form.fields['avocat'].disabled = True
    
    return render(request, 'rendezvous/rendezvous_form.html', {
        'form': form,
        'title': _('Nouveau rendez-vous')
    })

@login_required
@secretaire_required
def rendezvous_create_secretaire(request):
    if request.method == 'POST':
        form = RendezvousForm(request.POST)
        if form.is_valid():
            rendezvous = form.save()
            notifier_rendezvous(rendezvous, 'create')
            messages.success(request, _('Le rendez-vous a été créé avec succès.'))
            return redirect('rendezvous:detail', pk=rendezvous.pk)
    else:
        form = RendezvousForm()
    
    return render(request, 'rendezvous/rendezvous_form.html', {
        'form': form,
        'title': _('Nouveau rendez-vous')
    })

@login_required
@can_view_rendezvous
def rendezvous_detail(request, pk, **kwargs):
    rendezvous = kwargs.get('rendezvous')
    return render(request, 'rendezvous/rendezvous_detail.html', {'rendezvous': rendezvous})

@login_required
def rendezvous_update(request, pk):
    rendezvous = get_object_or_404(Rendezvous, pk=pk)
    if not (request.user.is_avocat or request.user.is_secretaire):
        return HttpResponseForbidden(_("Vous n'avez pas la permission de modifier ce rendez-vous."))
    
    if request.method == 'POST':
        form = RendezvousForm(request.POST, instance=rendezvous)
        if form.is_valid():
            form.save()
            notifier_rendezvous(rendezvous, 'update')
            messages.success(request, _('Le rendez-vous a été modifié avec succès.'))
            return redirect('rendezvous:detail', pk=rendezvous.pk)
    else:
        form = RendezvousForm(instance=rendezvous)
    
    return render(request, 'rendezvous/rendezvous_form.html', {
        'form': form,
        'title': _('Modifier le rendez-vous')
    })

@login_required
def rendezvous_delete(request, pk):
    rendezvous = get_object_or_404(Rendezvous, pk=pk)
    if not (request.user.is_avocat or request.user.is_secretaire):
        return HttpResponseForbidden(_("Vous n'avez pas la permission de supprimer ce rendez-vous."))
    
    if request.method == 'POST':
        notifier_rendezvous(rendezvous, 'delete')
        rendezvous.delete()
        messages.success(request, _('Le rendez-vous a été supprimé avec succès.'))
        return redirect('rendezvous:list')
    
    return render(request, 'rendezvous/rendezvous_confirm_delete.html', {'rendezvous': rendezvous})

@login_required
def rendezvous_confirm(request, pk):
    rendezvous = get_object_or_404(Rendezvous, pk=pk)
    if request.method == 'POST':
        if request.user.is_client and rendezvous.client.user != request.user:
            return HttpResponseForbidden(_("Vous n'avez pas la permission de confirmer ce rendez-vous."))
        
        # Update status directly in the database to bypass validation
        Rendezvous.objects.filter(pk=rendezvous.pk).update(
            statut=Rendezvous.Statut.CONFIRME,
            date_modification=timezone.now()
        )
        notifier_rendezvous(rendezvous, 'confirm')
        messages.success(request, _('Le rendez-vous a été confirmé.'))
        return redirect('rendezvous:detail', pk=rendezvous.pk)
    return redirect('rendezvous:detail', pk=rendezvous.pk)

@login_required
def rendezvous_cancel(request, pk):
    rendezvous = get_object_or_404(Rendezvous, pk=pk)
    if request.method == 'POST':
        if not (request.user.is_avocat or request.user.is_secretaire or 
                (request.user.is_client and rendezvous.client.user == request.user)):
            return HttpResponseForbidden(_("Vous n'avez pas la permission d'annuler ce rendez-vous."))
        
        rendezvous.statut = Rendezvous.Statut.ANNULE
        rendezvous.save()
        notifier_rendezvous(rendezvous, 'cancel')
        messages.success(request, _('Le rendez-vous a été annulé.'))
        return redirect('rendezvous:detail', pk=rendezvous.pk)
    return redirect('rendezvous:detail', pk=rendezvous.pk)

@login_required
def rendezvous_request(request):
    """View for clients to request appointments"""
    if not request.user.is_client:
        return HttpResponseForbidden(_("Seuls les clients peuvent demander des rendez-vous."))

    # Vérifier si l'utilisateur a un profil client
    if not hasattr(request.user, 'client') or request.user.client is None:
        from clients.models import Client
        try:
            # Essayer de trouver un profil client existant avec cet email
            client = Client.objects.get(email=request.user.email)
            # Si trouvé, lier ce profil à l'utilisateur
            client.user = request.user
            client.save()
            request.user.refresh_from_db()
        except Client.DoesNotExist:
            # Si aucun profil n'existe, en créer un nouveau
            Client.objects.create(
                user=request.user,
                nom=request.user.last_name,
                prenom=request.user.first_name,
                email=request.user.email,
                type_client='PAR',
                civilite='M'
            )
            request.user.refresh_from_db()

    if request.method == 'POST':
        form = RendezvousRequestForm(request.POST)
        if form.is_valid():
            rendezvous = form.save(commit=False)
            rendezvous.client = request.user.client
            rendezvous.statut = Rendezvous.Statut.EN_ATTENTE
            rendezvous.save()
            messages.success(request, _('Votre demande de rendez-vous a été envoyée avec succès.'))
            return redirect('rendezvous:detail', pk=rendezvous.pk)
    else:
        form = RendezvousRequestForm()
    return render(request, 'rendezvous/rendezvous_request.html', {
        'form': form,
        'title': _('Demander un rendez-vous')
    })

@login_required
def rendezvous_process(request, pk):
    """View for lawyers and secretaries to process appointment requests"""
    if not (request.user.is_avocat or request.user.is_secretaire):
        return HttpResponseForbidden(_("Vous n'avez pas la permission de traiter les demandes de rendez-vous."))
    
    rendezvous = get_object_or_404(Rendezvous, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'accept':
            avocat_id = request.POST.get('avocat')
            if avocat_id:
                rendezvous.avocat = Utilisateur.objects.get(id=avocat_id)
                rendezvous.statut = Rendezvous.Statut.PLANIFIE
                rendezvous.save()
                messages.success(request, _('Le rendez-vous a été accepté.'))
        
        elif action == 'refuse':
            form = RendezvousRefuseForm(request.POST, instance=rendezvous)
            if form.is_valid():
                rendezvous = form.save(commit=False)
                rendezvous.statut = Rendezvous.Statut.REFUSE
                rendezvous.save()
                messages.success(request, _('Le rendez-vous a été refusé.'))
        
        elif action == 'propose':
            form = RendezvousDatePropositionForm(request.POST, instance=rendezvous)
            if form.is_valid():
                rendezvous = form.save(commit=False)
                rendezvous.date_proposition = form.cleaned_data['date_proposition']
                rendezvous.save()
                messages.success(request, _('Une nouvelle date a été proposée.'))
        
        return redirect('rendezvous:detail', pk=rendezvous.pk)
    
    context = {
        'rendezvous': rendezvous,
        'avocats': Utilisateur.objects.filter(role='avocat'),
        'refuse_form': RendezvousRefuseForm(instance=rendezvous),
        'date_form': RendezvousDatePropositionForm(instance=rendezvous)
    }
    return render(request, 'rendezvous/rendezvous_process.html', context)

@login_required
def rendezvous_accept_date(request, pk):
    """View for clients to accept proposed dates"""
    rendezvous = get_object_or_404(Rendezvous, pk=pk)
    
    if not request.user.is_client or request.user.client != rendezvous.client:
        return HttpResponseForbidden(_("Vous n'avez pas la permission d'accepter cette date."))
    
    if request.method == 'POST' and rendezvous.date_proposition:
        rendezvous.date_debut = rendezvous.date_proposition
        rendezvous.date_fin = rendezvous.date_proposition + timezone.timedelta(hours=1)
        rendezvous.date_proposition = None
        rendezvous.statut = Rendezvous.Statut.PLANIFIE
        rendezvous.save()
        messages.success(request, _('La nouvelle date a été acceptée.'))
    
    return redirect('rendezvous:detail', pk=rendezvous.pk)
