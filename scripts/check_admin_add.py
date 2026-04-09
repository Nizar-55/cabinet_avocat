import os
import sys

BASE_DIR = os.getcwd()
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cabinet.settings')

import django
from django.test import Client

django.setup()

def main():
    client = Client()
    username = 'nizar'
    password = 'admin2004'
    logged = client.login(username=username, password=password)
    print('login:', logged)
    # Provide a valid Host header so Django allows the request from the test client
    resp = client.get('/admin/utilisateurs/utilisateur/add/', HTTP_HOST='127.0.0.1:8000')
    print('status_code:', resp.status_code)
    if resp.status_code >= 500:
        print('Server error response (truncated):')
        print(resp.content.decode('utf-8', errors='replace')[:2000])

if __name__ == '__main__':
    main()
