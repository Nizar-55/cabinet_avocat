import os
import sys
import traceback

# ensure project root on path
os.chdir(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cabinet.settings')
import django
django.setup()

from django.utils import timezone
from utilisateurs.models import Utilisateur
from dossiers.models import Dossier
from rendezvous.models import Rendezvous
from documents.models import Document
from django.core.exceptions import ObjectDoesNotExist

print('CWD:', os.getcwd())

try:
    now = timezone.now()
    print('now:', now)
except Exception:
    print('timezone error')
    traceback.print_exc()

# Check first user
try:
    u = Utilisateur.objects.first()
    if u:
        print('First user:', u.username, 'role:', u.role)
        print('is_avocat', u.is_avocat, 'is_secretaire', u.is_secretaire, 'is_client', u.is_client)
    else:
        print('No users found')
except Exception:
    print('Error fetching user:')
    traceback.print_exc()

# Run counts and role-specific filters
try:
    print('Dossier count:', Dossier.objects.count())
except Exception:
    print('Dossier query error:')
    traceback.print_exc()

try:
    print('Rendezvous count:', Rendezvous.objects.count())
except Exception:
    print('Rendezvous query error:')
    traceback.print_exc()

try:
    print('Document count:', Document.objects.count())
except Exception:
    print('Document query error:')
    traceback.print_exc()

# Try the home view logic for authenticated user if user exists
if u:
    try:
        stats = {}
        if u.is_avocat:
            stats = {
                'dossiers_actifs': Dossier.objects.filter(avocat=u, statut='EC').count(),
                'clients_total': 0,
            }
            print('avocat stats OK')
        elif u.is_secretaire:
            stats = {
                'rendezvous_jour': Rendezvous.objects.filter(date_debut__date=now.date()).count(),
            }
            print('secretaire stats OK')
        elif u.is_client:
            try:
                client = u.client
                print('client profile exists:', client)
            except ObjectDoesNotExist:
                print('client profile missing')
    except Exception:
        print('Error when computing stats:')
        traceback.print_exc()

print('done')
