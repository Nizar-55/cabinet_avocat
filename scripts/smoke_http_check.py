#!/usr/bin/env python
"""Simple smoke checker for common site paths using Django test client.

Run inside the venv:
.venv\Scripts\python.exe scripts\smoke_http_check.py
"""
import os
import sys

BASE_DIR = os.getcwd()
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cabinet.settings')

import django
from django.test import Client

django.setup()

PATHS = ['/', '/admin/', '/clients/', '/documents/']

def main():
    client = Client()
    # Use Host header allowed during dev
    ok = []
    for p in PATHS:
        resp = client.get(p, HTTP_HOST='127.0.0.1:8000')
        print(f'{p} -> {resp.status_code}')
        ok.append((p, resp.status_code))
    return 0

if __name__ == '__main__':
    main()
