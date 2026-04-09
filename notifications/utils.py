from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext as _
from django.template.loader import render_to_string
from django.utils import timezone
from .models import Notification

def envoyer_notification(destinataire, type_notif, titre, message, objet=None):
    """
    Crée une notification et envoie un email si configuré.
    """
    # Créer la notification
    notification = Notification.objects.create(
        destinataire=destinataire,
        type=type_notif,
        titre=titre,
        message=message,
        content_object=objet if objet else None
    )
    
    # Envoyer l'email si configuré
    if settings.EMAIL_ENABLED:
        context = {
            'titre': titre,
            'message': message,
            'date': timezone.now(),
            'destinataire': destinataire,
        }
        
        html_message = render_to_string('notifications/email.html', context)
        
        send_mail(
            subject=titre,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinataire.email],
            html_message=html_message
        )
    
    return notification

def notifier_rendezvous(rendezvous, action='create'):
    """
    Envoie une notification pour un rendez-vous.
    """
    if action == 'create':
        titre = _('Nouveau rendez-vous')
        message = _(
            'Un rendez-vous a été planifié pour le %(date)s à %(heure)s.\n'
            'Type: %(type)s\n'
            'Lieu: %(lieu)s\n'
            'Sujet: %(sujet)s'
        )
    elif action == 'update':
        titre = _('Rendez-vous modifié')
        message = _(
            'Le rendez-vous du %(date)s à %(heure)s a été modifié.\n'
            'Type: %(type)s\n'
            'Lieu: %(lieu)s\n'
            'Sujet: %(sujet)s'
        )
    elif action == 'delete':
        titre = _('Rendez-vous annulé')
        message = _(
            'Le rendez-vous du %(date)s à %(heure)s a été annulé.\n'
            'Type: %(type)s\n'
            'Sujet: %(sujet)s'
        )
    elif action == 'confirm':
        titre = _('Rendez-vous confirmé')
        message = _(
            'Le rendez-vous du %(date)s à %(heure)s a été confirmé.\n'
            'Type: %(type)s\n'
            'Lieu: %(lieu)s\n'
            'Sujet: %(sujet)s'
        )
    elif action == 'cancel':
        titre = _('Rendez-vous annulé')
        message = _(
            'Le rendez-vous du %(date)s à %(heure)s a été annulé.\n'
            'Type: %(type)s\n'
            'Sujet: %(sujet)s'
        )
    else:
        return  # Action non reconnue
    
    message = message % {
        'date': rendezvous.date_debut.strftime('%d/%m/%Y'),
        'heure': rendezvous.date_debut.strftime('%H:%M'),
        'type': rendezvous.get_type_display(),
        'lieu': rendezvous.lieu,
        'sujet': rendezvous.sujet,
    }
    
    # Notifier le client
    if rendezvous.client and rendezvous.client.user:
        envoyer_notification(
            destinataire=rendezvous.client.user,
            type_notif=Notification.Type.RENDEZVOUS,
            titre=titre,
            message=message,
            objet=rendezvous
        )
    
    # Notifier l'avocat
    if rendezvous.avocat:
        envoyer_notification(
            destinataire=rendezvous.avocat,
            type_notif=Notification.Type.RENDEZVOUS,
            titre=titre,
            message=message,
            objet=rendezvous
        )

def notifier_document(document, action='creation'):
    """
    Envoie une notification pour un document.
    """
    if action == 'creation':
        titre = _('Nouveau document')
        message = _(
            'Un nouveau document a été créé:\n'
            'Titre: %(titre)s\n'
            'Type: %(type)s\n'
            'Dossier: %(dossier)s'
        )
    else:  # modification
        titre = _('Document modifié')
        message = _(
            'Le document a été modifié:\n'
            'Titre: %(titre)s\n'
            'Type: %(type)s\n'
            'Dossier: %(dossier)s'
        )
    
    message = message % {
        'titre': document.titre,
        'type': document.get_type_document_display(),
        'dossier': document.dossier,
    }
    
    # Notifier l'avocat responsable du dossier
    if document.dossier and document.dossier.avocat:
        envoyer_notification(
            destinataire=document.dossier.avocat,
            type_notif=Notification.Type.DOCUMENT,
            titre=titre,
            message=message,
            objet=document
        ) 