import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cabinet.settings')
django.setup()

from django.utils import timezone
from clients.models import Client
from utilisateurs.models import Utilisateur
from rendezvous.models import Rendezvous
from dossiers.models import Dossier
from datetime import datetime, timedelta

def create_test_data():
    # Get or create a test client
    client, created = Client.objects.get_or_create(
        email='test.client3@example.com',
        defaults={
            'civilite': 'M',
            'nom': 'Test',
            'prenom': 'Client',
            'telephone': '+212612345678',
            'adresse': '123 Rue Mohammed V',
            'code_postal': '10000',
            'ville': 'Rabat',
            'pays': 'Maroc'
        }
    )
    if created:
        print(f"Created test client: {client}")
    else:
        print(f"Using existing client: {client}")

    # Get the first superuser
    avocat = Utilisateur.objects.filter(is_superuser=True).first()
    if not avocat:
        print("No superuser found. Please create one first.")
        return

    # Get or create a test dossier
    dossier, created = Dossier.objects.get_or_create(
        client=client,
        defaults={
            'titre': "Dossier test",
            'description': "Description du dossier test",
            'statut': 'EC'  # En cours
        }
    )
    if created:
        print(f"Created test dossier: {dossier}")
    else:
        print(f"Using existing dossier: {dossier}")

    # Create a test rendez-vous with a specific date
    tomorrow_10am = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0) + timedelta(days=1)
    rdv = Rendezvous.objects.create(
        client=client,
        avocat=avocat,
        dossier=dossier,
        type='CO',  # Consultation
        date_debut=tomorrow_10am,
        date_fin=tomorrow_10am + timedelta(hours=1),
        lieu='Cabinet',
        sujet='Test consultation',
        description='Test consultation description'
    )
    print(f"Created test rendez-vous: {rdv}")

if __name__ == '__main__':
    create_test_data() 