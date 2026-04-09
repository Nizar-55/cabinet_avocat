import urllib.request
import urllib.error

BASE = 'http://127.0.0.1:8000'
PATHS = ['/', '/admin/', '/_style_guide/', '/clients/', '/documents/', '/dossiers/', '/rendezvous/']

results = []
for p in PATHS:
    url = BASE + p
    try:
        r = urllib.request.urlopen(url, timeout=5)
        code = r.getcode()
        results.append((p, code, 'OK'))
    except urllib.error.HTTPError as e:
        results.append((p, e.code, 'HTTPError'))
    except Exception as e:
        results.append((p, None, repr(e)))

print('Smoke check results:')
for p, code, info in results:
    print(f"{p:15} -> {code!s:5} {info}")

# Exit non-zero if any major failure (no code)
fail = any(code is None for _, code, _ in results)
if fail:
    raise SystemExit(1)
