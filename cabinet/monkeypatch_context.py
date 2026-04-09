"""Apply a runtime monkeypatch to Django's template Context copying
to be compatible across Python versions without editing site-packages.

This module will be imported from `cabinet.__init__` so it runs early.
"""
from copy import copy

def _safe_basecontext_copy(self):
    # Create new instance without calling __init__, copy attributes
    duplicate = object.__new__(self.__class__)
    try:
        duplicate.__dict__ = self.__dict__.copy()
    except Exception:
        duplicate.dicts = self.dicts[:]
        return duplicate
    duplicate.dicts = self.dicts[:]
    return duplicate

def apply_patch():
    try:
        import django.template.context as _ctx
    except Exception:
        return False

    # Only patch if the original exists and hasn't been patched yet
    BaseContext = getattr(_ctx, 'BaseContext', None)
    if BaseContext is None:
        return False
    if getattr(BaseContext, '__copy__', None) is _safe_basecontext_copy:
        return True
    BaseContext.__copy__ = _safe_basecontext_copy
    return True

apply_patch()
