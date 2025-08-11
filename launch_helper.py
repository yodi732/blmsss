
# helper to ensure 'app' exists in main or app module
import importlib, sys, os
try:
    # try import main.app or app in top-level
    if 'app' not in globals():
        try:
            m = importlib.import_module('main')
            app = getattr(m, 'app', None)
        except Exception:
            pass
    if 'app' not in globals() or app is None:
        # fallback: import app from current app.py (this file may be replaced)
        from app import app as _app  # noqa
except Exception:
    pass
