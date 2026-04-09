from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Count, Sum, Q
from django.http import HttpResponseForbidden
from django.db import DatabaseError
from django.contrib import messages
from dossiers.models import Dossier
from rendezvous.models import Rendezvous
from documents.models import Document
from clients.models import Client
from django.contrib.auth.forms import AuthenticationForm
from utilisateurs.forms import ClientInscriptionForm
from utilisateurs.models import LawCategory
from utilisateurs.decorators import avocat_required, secretaire_required, client_required
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import login
from datetime import timedelta
from .models import User, SystemAlert, ActivityLog
import traceback

@login_required
def dashboard(request):
    try:
        # Get current date and next week
        now = timezone.now()
        next_week = now + timezone.timedelta(days=7)
        
        # Base context
        context = {}
        
        if request.user.is_avocat:
            # Statistiques pour les avocats (uniquement leurs dossiers et clients)
            try:
                stats = {
                    'dossiers_actifs': Dossier.objects.filter(
                        avocat=request.user,
                        statut='EC'
                    ).count(),
                    'clients_total': Client.objects.filter(
                        dossiers__avocat=request.user
                    ).distinct().count(),
                    'rendezvous_jour': Rendezvous.objects.filter(
                        date_debut__date=now.date(),
                        avocat=request.user,
                        statut__in=['PL', 'CO']
                    ).count(),
                    'documents_attente': Document.objects.filter(
                        dossier__avocat=request.user,
                        statut='AT'
                    ).count(),
                }
                
                # Rendez-vous du jour (uniquement leurs rendez-vous)
                rendezvous_jour = Rendezvous.objects.filter(
                    date_debut__date=now.date(),
                    avocat=request.user,
                    statut__in=['PL', 'CO']
                ).order_by('date_debut')
                
                # Documents en attente (uniquement leurs documents)
                documents_attente = Document.objects.filter(
                    dossier__avocat=request.user,
                    statut='AT'
                ).order_by('-date_creation')[:5]
                
                # Dossiers actifs (uniquement leurs dossiers)
                dossiers_actifs = Dossier.objects.filter(
                    avocat=request.user,
                    statut='EC'
                ).order_by('-date_modification')[:5]
                
                # Derniers clients ajoutés
                derniers_clients = Client.objects.filter(
                    dossiers__avocat=request.user
                ).distinct().order_by('-date_creation')[:5]
                
                context.update({
                    'stats': stats,
                    'rendezvous_jour': rendezvous_jour,
                    'documents_attente': documents_attente,
                    'dossiers_actifs': dossiers_actifs,
                    'derniers_clients': derniers_clients,
                })
                
            except DatabaseError:
                messages.error(request, _("Une erreur est survenue lors de la récupération des données. Veuillez réessayer."))
                context.update({
                    'stats': {'dossiers_actifs': 0, 'clients_total': 0, 'rendezvous_jour': 0, 'documents_attente': 0},
                    'rendezvous_jour': [],
                    'documents_attente': [],
                    'dossiers_actifs': [],
                    'derniers_clients': [],
                })
            
            return render(request, 'dashboard/avocat_dashboard.html', context)
            
        elif request.user.is_secretaire:
            try:
                # Statistiques pour les secrétaires
                try:
                    messages_non_lus = request.user.notifications.filter(
                        date_lecture__isnull=True
                    ).count()
                except ObjectDoesNotExist:
                    messages_non_lus = 0
                    
                stats = {
                    'rendezvous_jour': Rendezvous.objects.filter(
                        date_debut__date=now.date(),
                        statut__in=['PL', 'CO']
                    ).count(),
                    'documents_a_traiter': Document.objects.filter(
                        statut='BR'  # Brouillon
                    ).count(),
                    'taches_en_attente': Document.objects.filter(
                        statut='AT'  # En attente
                    ).count(),
                    'messages_non_lus': messages_non_lus,
                }
                
                # Rendez-vous du jour (tous les rendez-vous du cabinet)
                rendezvous_jour = Rendezvous.objects.filter(
                    date_debut__date=now.date(),
                    statut__in=['PL', 'CO']
                ).order_by('date_debut')
                
                # Documents à traiter
                documents_a_traiter = Document.objects.filter(
                    statut='BR'
                ).order_by('-date_creation')[:5]
                
                # Derniers dossiers modifiés
                derniers_dossiers = Dossier.objects.all().order_by('-date_modification')[:5]
                
                context.update({
                    'stats': stats,
                    'rendezvous_jour': rendezvous_jour,
                    'documents_a_traiter': documents_a_traiter,
                    'derniers_dossiers': derniers_dossiers,
                })
                
            except DatabaseError:
                messages.error(request, _("Une erreur est survenue lors de la récupération des données. Veuillez réessayer."))
                context.update({
                    'stats': {'rendezvous_jour': 0, 'documents_a_traiter': 0, 'taches_en_attente': 0, 'messages_non_lus': 0},
                    'rendezvous_jour': [],
                    'documents_a_traiter': [],
                    'derniers_dossiers': [],
                })
            
            return render(request, 'dashboard/secretaire_dashboard.html', context)
            
        elif request.user.is_client:
            try:
                client = request.user.client
                try:
                    messages_non_lus = request.user.notifications.filter(
                        date_lecture__isnull=True
                    ).count()
                except ObjectDoesNotExist:
                    messages_non_lus = 0
                    
                # Statistiques pour les clients
                stats = {
                    'dossiers_total': Dossier.objects.filter(client=client).count(),
                    'prochains_rdv': Rendezvous.objects.filter(
                        client=client,
                        date_debut__gte=now,
                        statut__in=['PL', 'CO']
                    ).count(),
                    'documents_recus': Document.objects.filter(
                        dossier__client=client,
                        statut='VA'  # Validé
                    ).count(),
                    'messages_non_lus': messages_non_lus,
                }
                
                # Prochains rendez-vous
                prochains_rdv = Rendezvous.objects.filter(
                    client=client,
                    date_debut__gte=now,
                    statut__in=['PL', 'CO']
                ).order_by('date_debut')[:5]
                
                # Derniers documents
                derniers_documents = Document.objects.filter(
                    dossier__client=client,
                    statut='VA'
                ).order_by('-date_creation')[:5]
                
                # Dossiers en cours
                dossiers_en_cours = Dossier.objects.filter(
                    client=client,
                    statut='EC'
                ).order_by('-date_modification')[:5]
                
                context.update({
                    'stats': stats,
                    'prochains_rdv': prochains_rdv,
                    'derniers_documents': derniers_documents,
                    'dossiers_en_cours': dossiers_en_cours,
                })
                
            except ObjectDoesNotExist:
                return HttpResponseForbidden(_("Votre profil client n'est pas configuré correctement. Veuillez contacter l'administration."))
            except DatabaseError:
                messages.error(request, _("Une erreur est survenue lors de la récupération des données. Veuillez réessayer."))
                context.update({
                    'stats': {'dossiers_total': 0, 'prochains_rdv': 0, 'documents_recus': 0, 'messages_non_lus': 0},
                    'prochains_rdv': [],
                    'derniers_documents': [],
                    'dossiers_en_cours': [],
                })
            
            return render(request, 'dashboard/client_dashboard.html', context)
        
        # If user has no specific role, show generic dashboard
        return render(request, 'dashboard.html', context)
        
    except Exception as e:
        messages.error(request, _("Une erreur inattendue est survenue. Veuillez réessayer."))
        return redirect('home')

def home(request):
    try:
        # Ensure stats is always defined (anonymous users may hit home)
        stats = {}
        if request.user.is_authenticated:
            # Récupérer les statistiques en fonction du rôle de l'utilisateur
            now = timezone.now()
            
            if request.user.is_avocat:
                stats = {
                    'dossiers_actifs': Dossier.objects.filter(avocat=request.user, statut='EC').count(),
                    'clients_total': Client.objects.filter(dossiers__avocat=request.user).distinct().count(),
                    'rendezvous_jour': Rendezvous.objects.filter(date_debut__date=now.date(), avocat=request.user).count(),
                    'documents_attente': Document.objects.filter(dossier__avocat=request.user, statut='AT').count()
                }
            elif request.user.is_secretaire:
                stats = {
                    'rendezvous_jour': Rendezvous.objects.filter(date_debut__date=now.date()).count(),
                    'documents_a_traiter': Document.objects.filter(statut='BR').count(),
                    'taches_en_attente': Document.objects.filter(statut='AT').count()
                }
            elif request.user.is_client:
                try:
                    client = request.user.client
                    stats = {
                        'dossiers_total': Dossier.objects.filter(client=client).count(),
                        'prochains_rdv': Rendezvous.objects.filter(client=client, date_debut__gte=now).count(),
                        'documents_recus': Document.objects.filter(dossier__client=client, statut='VA').count()
                    }
                except ObjectDoesNotExist:
                    stats = {}

        if request.method == 'POST':
            if 'register_form' in request.POST:
                form = ClientInscriptionForm(request.POST)
                if form.is_valid():
                    user = form.save()
                    messages.success(request, _("Votre compte a été créé avec succès."))
                    login(request, user)
                    return redirect('home')
                else:
                    context = {
                        'login_form': AuthenticationForm(),
                        'register_form': form,
                        'law_categories': LawCategory.objects.all(),
                        'active_tab': 'register',
                        'stats': stats
                    }
                    return render(request, 'home.html', context)
            else:
                form = AuthenticationForm(data=request.POST)
                if form.is_valid():
                    user = form.get_user()
                    login(request, user)
                    messages.success(request, _('Connexion réussie.'))
                    return redirect('home')
                else:
                    context = {
                        'login_form': form,
                        'register_form': ClientInscriptionForm(),
                        'law_categories': LawCategory.objects.all(),
                        'active_tab': 'login',
                        'stats': stats
                    }
                    return render(request, 'home.html', context)

        context = {
            'login_form': AuthenticationForm(),
            'register_form': ClientInscriptionForm(),
            'law_categories': LawCategory.objects.all(),
            'stats': stats
        }
        return render(request, 'home.html', context)
    except Exception as e:
        # Log the traceback to console for debugging
        traceback.print_exc()
        messages.error(request, _("Une erreur est survenue lors du chargement de la page d'accueil."))
        return render(request, 'home.html', {'error': True})

def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def admin_dashboard(request):
    # Obtenir la date d'aujourd'hui
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)

    # Statistiques générales
    stats = {
        'total_users': User.objects.count(),
        'new_users_today': User.objects.filter(date_joined__date=today).count(),
        'total_dossiers': Dossier.objects.count(),
        'active_dossiers': Dossier.objects.filter(statut='EN_COURS').count(),
        'total_rdv': Rendezvous.objects.count(),
        'rdv_today': Rendezvous.objects.filter(date_debut__date=today).count(),
        'total_documents': Document.objects.count(),
        'pending_documents': Document.objects.filter(statut='EN_ATTENTE').count(),
    }

    # Dernières activités
    recent_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:10]

    # Alertes système
    system_alerts = SystemAlert.objects.filter(
        resolved=False
    ).order_by('-level', '-timestamp')[:5]

    # Données pour le graphique mensuel
    monthly_data = Dossier.objects.filter(
        date_creation__gte=thirty_days_ago
    ).extra(
        select={'day': 'date(date_creation)'}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')

    monthly_rdv = Rendezvous.objects.filter(
        date_debut__gte=thirty_days_ago
    ).extra(
        select={'day': 'date(date_debut)'}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')

    # Préparer les données pour les graphiques
    dates = [(today - timedelta(days=x)).strftime('%d/%m') for x in range(30, -1, -1)]
    dossiers_counts = [0] * 31
    rdv_counts = [0] * 31

    for entry in monthly_data:
        day_diff = (today - entry['day']).days
        if 0 <= day_diff <= 30:
            dossiers_counts[30 - day_diff] = entry['count']

    for entry in monthly_rdv:
        day_diff = (today - entry['day']).days
        if 0 <= day_diff <= 30:
            rdv_counts[30 - day_diff] = entry['count']

    # Données pour le graphique de répartition des dossiers
    dossiers_status = Dossier.objects.values('statut').annotate(
        count=Count('id')
    ).order_by('statut')

    dossiers_status_labels = [d['statut'] for d in dossiers_status]
    dossiers_status_data = [d['count'] for d in dossiers_status]

    context = {
        'stats': stats,
        'recent_activities': recent_activities,
        'system_alerts': system_alerts,
        'monthly_labels': dates,
        'monthly_dossiers': dossiers_counts,
        'monthly_rdv': rdv_counts,
        'dossiers_status_labels': dossiers_status_labels,
        'dossiers_status_data': dossiers_status_data,
    }

    return render(request, 'admin/dashboard.html', context)

@user_passes_test(lambda u: u.is_superuser)
def activity_log(request):
    activities = ActivityLog.objects.select_related('user').order_by('-timestamp')
    return render(request, 'admin/activity_log.html', {'activities': activities})

@user_passes_test(lambda u: u.is_superuser)
def system_alerts(request):
    alerts = SystemAlert.objects.all().order_by('-level', '-timestamp')
    if request.method == 'POST' and 'alert_id' in request.POST:
        alert_id = request.POST['alert_id']
        try:
            alert = SystemAlert.objects.get(id=alert_id)
            alert.resolve(request.user)
            messages.success(request, _('Alerte marquée comme résolue.'))
        except SystemAlert.DoesNotExist:
            messages.error(request, _('Alerte introuvable.'))
    return render(request, 'admin/system_alerts.html', {'alerts': alerts}) 