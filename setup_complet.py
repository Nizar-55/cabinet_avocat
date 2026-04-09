import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cabinet.settings')
django.setup()

from django.utils import timezone
from utilisateurs.models import Utilisateur
from clients.models import Client
from dossiers.models import Dossier
from django.db import transaction

def setup_complet():
    print("=== Configuration complète du système ===")
    
    # 1. Configurer l'utilisateur admin
    try:
        admin = Utilisateur.objects.get(username='admin')
        admin.role = 'avocat'
        admin.is_staff = True
        admin.is_superuser = True
        admin.first_name = "Admin"
        admin.last_name = "Cabinet"
        admin.save()
        print("✓ Admin utilisateur mis à jour")
    except Utilisateur.DoesNotExist:
        admin = Utilisateur.objects.create_superuser(
            username='admin',
            email='admin@cabinet.com',
            password='admin123',
            role='avocat',
            first_name="Admin",
            last_name="Cabinet"
        )
        print("✓ Admin utilisateur créé")

    # 2. Créer un client de test
    with transaction.atomic():
        client, created = Client.objects.get_or_create(
            email='client.test@cabinet.com',
            defaults={
                'civilite': 'M',
                'nom': 'Client',
                'prenom': 'Test',
                'telephone': '+212600000000',
                'adresse': '123 Avenue Hassan II',
                'code_postal': '20000',
                'ville': 'Casablanca',
                'pays': 'Maroc',
                'type_client': 'PAR'  # Particulier
            }
        )
        if created:
            print("✓ Client test créé")
        else:
            print("✓ Client test existant")

        # 3. Créer un dossier de test
        dossier, created = Dossier.objects.get_or_create(
            client=client,
            titre="Dossier Test",
            defaults={
                'description': "Dossier de test pour le système",
                'statut': 'EC',  # En cours
                'notes': "Dossier créé automatiquement pour les tests"
            }
        )
        if created:
            print("✓ Dossier test créé")
        else:
            print("✓ Dossier test existant")

    print("\nConfiguration terminée !")
    print("\nVous pouvez maintenant :")
    print("1. Vous connecter avec :")
    print("   - Nom d'utilisateur : admin")
    print("   - Mot de passe : admin123")
    print("\n2. Créer des documents en utilisant :")
    print(f"   - Dossier : {dossier.reference} - {dossier.titre}")
    print("\n3. Créer des rendez-vous avec :")
    print(f"   - Client : {client.nom} {client.prenom}")
    print(f"   - Dossier : {dossier.reference}")

if __name__ == '__main__':
    setup_complet() 