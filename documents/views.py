from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.http import HttpResponseForbidden
from .models import Document, DocumentVersion
from .forms import DocumentForm, DocumentVersionForm
from notifications.utils import notifier_document
from utilisateurs.decorators import can_view_document as document_access_required, avocat_required, secretaire_required

def can_view_document(user, document):
    """Vérifie si l'utilisateur peut voir le document"""
    if user.is_avocat:
        return True  # Les avocats peuvent voir tous les documents
    elif user.is_secretaire:
        return True  # La secrétaire peut voir tous les documents du cabinet
    elif user.is_client:
        return document.dossier.client.user == user
    return False

@login_required
def document_list(request):
    if request.user.is_avocat:
        # Les avocats peuvent voir tous les documents
        documents = Document.objects.all()
    elif request.user.is_secretaire:
        # Les secrétaires peuvent voir tous les documents
        documents = Document.objects.all()
    elif request.user.is_client:
        # Les clients ne voient que leurs documents validés
        documents = Document.objects.filter(
            dossier__client__user=request.user,
            statut='VA'  # Uniquement les documents validés
        )
    else:
        return HttpResponseForbidden(_("Vous n'avez pas accès à cette page."))
        
    documents = documents.order_by('-date_creation')
    return render(request, 'documents/document_list.html', {'documents': documents})

@login_required
@avocat_required
def document_create(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.createur = request.user
            document.statut = 'VA'  # Les avocats créent directement des documents validés
            document.save()
            
            # Créer la première version du document
            DocumentVersion.objects.create(
                document=document,
                fichier=document.fichier,
                createur=request.user,
                numero_version=1,
                commentaire=_("Version initiale")
            )
            
            notifier_document(document, 'create')
            messages.success(request, _('Le document a été créé avec succès.'))
            return redirect('documents:detail', reference=document.reference)
    else:
        form = DocumentForm()
        # Filtrer les dossiers accessibles à l'avocat
        form.fields['dossier'].queryset = form.fields['dossier'].queryset.filter(avocat=request.user)
    
    return render(request, 'documents/document_form.html', {
        'form': form,
        'title': _('Nouveau document')
    })

@login_required
@document_access_required
def document_detail(request, reference, **kwargs):
    document = kwargs.get('document')
    return render(request, 'documents/document_detail.html', {'document': document})

@login_required
@document_access_required
def document_update(request, reference, **kwargs):
    document = kwargs.get('document')
    if not (request.user.is_avocat or request.user.is_secretaire):
        return HttpResponseForbidden(_("Vous n'avez pas la permission de modifier ce document."))
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            document = form.save()
            if request.FILES.get('fichier'):
                # Créer une nouvelle version
                derniere_version = document.versions.order_by('-numero_version').first()
                nouvelle_version = DocumentVersion.objects.create(
                    document=document,
                    fichier=document.fichier,
                    createur=request.user,
                    numero_version=derniere_version.numero_version + 1 if derniere_version else 1,
                    commentaire=form.cleaned_data.get('commentaire', _("Mise à jour"))
                )
                document.version = nouvelle_version.numero_version
                document.save()
            
            notifier_document(document, 'update')
            messages.success(request, _('Le document a été modifié avec succès.'))
            return redirect('documents:detail', reference=document.reference)
    else:
        form = DocumentForm(instance=document)
        if request.user.is_avocat:
            form.fields['dossier'].queryset = form.fields['dossier'].queryset.filter(avocat=request.user)
    
    return render(request, 'documents/document_form.html', {
        'form': form,
        'document': document,
        'title': _('Modifier le document')
    })

@login_required
@avocat_required
def document_validate(request, reference):
    document = get_object_or_404(Document, reference=reference, dossier__avocat=request.user)
    if request.method == 'POST':
        document.statut = 'VA'
        document.date_validation = timezone.now()
        document.validateur = request.user
        document.save()
        notifier_document(document, 'validate')
        messages.success(request, _('Le document a été validé avec succès.'))
        return redirect('documents:detail', reference=document.reference)
    return render(request, 'documents/document_validate.html', {'document': document})

@login_required
@document_access_required
def document_delete(request, reference, **kwargs):
    document = kwargs.get('document')
    if not (request.user.is_avocat or request.user.is_secretaire):
        return HttpResponseForbidden(_("Vous n'avez pas la permission de supprimer ce document."))
    
    if request.method == 'POST':
        notifier_document(document, 'delete')
        document.delete()
        messages.success(request, _('Le document a été supprimé avec succès.'))
        return redirect('documents:list')
    
    return render(request, 'documents/document_confirm_delete.html', {'document': document})

@login_required
@document_access_required
def document_versions(request, reference, **kwargs):
    document = kwargs.get('document')
    versions = document.versions.all().order_by('-numero_version')
    return render(request, 'documents/document_versions.html', {
        'document': document,
        'versions': versions
    })

@login_required
@document_access_required
def document_version_create(request, reference, **kwargs):
    document = kwargs.get('document')
    if not (request.user.is_avocat or request.user.is_secretaire):
        return HttpResponseForbidden(_("Vous n'avez pas la permission de créer des versions."))
    
    if request.method == 'POST':
        form = DocumentVersionForm(request.POST, request.FILES)
        if form.is_valid():
            derniere_version = document.versions.order_by('-numero_version').first()
            version = form.save(commit=False)
            version.document = document
            version.createur = request.user
            version.numero_version = derniere_version.numero_version + 1 if derniere_version else 1
            version.save()
            
            document.fichier = version.fichier
            document.version = version.numero_version
            document.save()
            
            messages.success(request, _('La nouvelle version a été créée avec succès.'))
            notifier_document(document, 'version')
            return redirect('documents:versions', reference=document.reference)
    else:
        form = DocumentVersionForm()
    
    return render(request, 'documents/document_version_form.html', {
        'form': form,
        'document': document,
        'title': _('Nouvelle version')
    })
