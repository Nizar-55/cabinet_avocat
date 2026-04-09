from utilisateurs.models import Utilisateur
from clients.models import Client
from django.db import transaction

# Script to link all Utilisateur with role 'client' to a Client object if missing
def link_clients():
    count = 0
    for user in Utilisateur.objects.filter(role='client'):
        if not hasattr(user, 'client') or user.client is None:
            # Use user info for Client fields, fallback to empty if missing
            client = Client.objects.create(
                user=user,
                nom=user.last_name or 'Nom',
                prenom=user.first_name or 'Prénom',
                email=user.email or f'client{user.id}@example.com',
                telephone=user.telephone or '',
            )
            count += 1
    print(f"{count} client(s) linked.")

if __name__ == "__main__":
    with transaction.atomic():
        link_clients()
