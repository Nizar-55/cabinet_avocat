from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Client
from .forms import ClientForm
import logging
from django.views.decorators.http import require_POST
from dossiers.models import Dossier
from django.db.models.deletion import ProtectedError

logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def client_list(request):
    clients = Client.objects.all().order_by('nom', 'prenom')
    return render(request, 'clients/client_list.html', {'clients': clients})

@login_required
def client_create(request):
    logger.debug('Tentative de création d\'un client')
    if request.method == 'POST':
        logger.debug('Méthode POST reçue avec les données: %s', request.POST)
        form = ClientForm(request.POST)
        if form.is_valid():
            logger.debug('Formulaire valide')
            client = form.save()
            messages.success(request, _('Le client a été créé avec succès.'))
            return redirect('clients:detail', pk=client.pk)
        else:
            logger.error('Erreurs dans le formulaire: %s', form.errors)
    else:
        form = ClientForm()
    return render(request, 'clients/client_form.html', {'form': form, 'title': _('Nouveau client')})

@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    return render(request, 'clients/client_detail.html', {'client': client})

@login_required
def client_update(request, pk):
    logger.debug('Tentative de modification du client %s', pk)
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        logger.debug('Méthode POST reçue avec les données: %s', request.POST)
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            logger.debug('Formulaire valide')
            form.save()
            messages.success(request, _('Le client a été modifié avec succès.'))
            return redirect('clients:detail', pk=client.pk)
        else:
            logger.error('Erreurs dans le formulaire: %s', form.errors)
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/client_form.html', {
        'form': form,
        'client': client,
        'title': _('Modifier le client')
    })

@login_required
def client_delete(request, pk):
    logger.debug('Tentative de suppression du client %s', pk)
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        logger.debug('Méthode POST reçue pour la suppression')
        try:
            client.delete()
            messages.success(request, _('Le client a été supprimé avec succès.'))
            return redirect('clients:list')
        except Exception as e:
            from django.db.models.deletion import ProtectedError
            if isinstance(e, ProtectedError):
                messages.error(request, _("Impossible de supprimer ce client car il possède des dossiers liés. Supprimez ou réassignez d'abord les dossiers."))
                return redirect('clients:detail', pk=client.pk)
            else:
                messages.error(request, _('Erreur lors de la suppression du client.'))
                return redirect('clients:detail', pk=client.pk)
    return render(request, 'clients/client_confirm_delete.html', {'client': client})

@require_POST
@login_required
def delete_dossiers(request, pk):
    client = get_object_or_404(Client, pk=pk)
    dossiers = client.dossiers.all()
    try:
        if dossiers.exists():
            # If cascading delete requested, delete related documents first
            if request.GET.get('delete_documents') == '1':
                for dossier in dossiers:
                    for doc in getattr(dossier, 'documents', []).all():
                        doc.delete()
                dossiers.delete()
                messages.success(request, _('Tous les dossiers et documents liés du client ont été supprimés.'))
            else:
                dossiers.delete()
                messages.success(request, _('Tous les dossiers du client ont été supprimés.'))
        else:
            messages.info(request, _('Aucun dossier à supprimer pour ce client.'))
    except ProtectedError as e:
        # Get blocking objects (e.g., documents)
        blocking_objects = e.protected_objects
        messages.error(request, _('Impossible de supprimer certains dossiers car ils sont liés à des documents ou d’autres objets protégés.'))
        return render(request, 'clients/client_confirm_delete.html', {
            'client': client,
            'blocking_objects': blocking_objects,
        })
    return redirect('clients:delete', pk=client.pk)
