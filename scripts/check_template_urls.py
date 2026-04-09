#!/usr/bin/env python
"""Scan templates for `{% url 'name' %}` tags and attempt to reverse them.

Run this from the project root inside the venv:
    .venv/Scripts/python.exe scripts/check_template_urls.py
"""
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cabinet.settings')

import django
from django.urls import reverse, NoReverseMatch

django.setup()

TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

url_tag_re = re.compile(r"{%\s*url\s+['\"](?P<name>[^'\"]+)['\"](?P<rest>[^%}]*)%}")
kw_re = re.compile(r"(?P<kw>\w+)\s*=\s*[^\s)]+")

def find_template_files(root):
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith('.html'):
                yield os.path.join(dirpath, fn)

def extract_url_tags(text):
    for m in url_tag_re.finditer(text):
        name = m.group('name')
        rest = m.group('rest') or ''
        kwargs = [g.group('kw') for g in kw_re.finditer(rest)]
        yield name, kwargs

def try_reverse(name, kwargs):
    # Try simple attempts: no args, one positional, kwargs with '1'
    attempts = []
    try:
        reverse(name)
        return True, 'ok (no args)'
    except NoReverseMatch as e:
        attempts.append(str(e))

    try:
        reverse(name, args=('1',))
        return True, "ok (positional '1')"
    except NoReverseMatch as e:
        attempts.append(str(e))

    # Try kwargs if we have keys
    if kwargs:
        kwvals = {k: '1' for k in kwargs}
        try:
            reverse(name, kwargs=kwvals)
            return True, f"ok (kwargs={list(kwvals.keys())})"
        except NoReverseMatch as e:
            attempts.append(str(e))

    return False, '; '.join(attempts[:2])

def main():
    if not os.path.isdir(TEMPLATE_DIR):
        print('Templates directory not found:', TEMPLATE_DIR)
        sys.exit(2)

    found = {}
    for path in find_template_files(TEMPLATE_DIR):
        with open(path, 'r', encoding='utf-8') as f:
            txt = f.read()
        for name, kwargs in extract_url_tags(txt):
            entry = found.setdefault(name, {'files': set(), 'kwargs': set()})
            entry['files'].add(path.replace(os.getcwd() + os.sep, ''))
            for k in kwargs:
                entry['kwargs'].add(k)

    ok = []
    bad = []
    for name, info in sorted(found.items()):
        kwlist = list(info['kwargs'])
        ok_flag, msg = try_reverse(name, kwlist)
        if ok_flag:
            ok.append((name, msg, sorted(info['files'])))
        else:
            bad.append((name, msg, sorted(info['files'])))

    print('\nTemplate URL check summary:')
    print(f'  Found {len(found)} distinct url() usages in templates')
    print(f'  Resolved: {len(ok)}')
    print(f'  Unresolved: {len(bad)}\n')

    if ok:
        print('Resolved (examples):')
        for name, msg, files in ok[:20]:
            print(f' - {name}: {msg}  (used in {files[0]})')
    if bad:
        print('\nUnresolved or failing reverses:')
        for name, msg, files in bad:
            print(f' - {name}: {msg}')
            for p in files:
                print(f'    used in {p}')

    if bad:
        print('\nSome template url() tags could not be reversed automatically.\n' \
              'If a pattern requires dynamic args, this script may report it as unresolved.\n' \
              'Review the listed template files and ensure the named URL exists or adjust tests accordingly.')
        sys.exit(1)
    else:
        print('All template url() names resolved (or resolved with dummy args).')
        sys.exit(0)

if __name__ == '__main__':
    main()
