import os, sys
os.chdir(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cabinet.settings')
import django
django.setup()

from django.test import Client
from utilisateurs.models import Utilisateur

c = Client()
user = Utilisateur.objects.first()
if user:
    c.force_login(user)
    resp = c.get('/', HTTP_HOST='127.0.0.1')
    print('status:', resp.status_code)
    print('template names:', getattr(resp, 'templates', None))
    content = resp.content.decode('utf-8', errors='replace')
    # print a slice of content around the message
    if 'Une erreur est survenue' in content:
        idx = content.find('Une erreur est survenue')
        print(content[max(0, idx-200):idx+800])
    else:
        print(content[:1000])
else:
    print('No user found')
