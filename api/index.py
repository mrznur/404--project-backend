"""
Vercel serverless entry point for Django.
Vercel looks for api/index.py and calls the WSGI app.
"""
import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ.setdefault('VERCEL', '1')

# Run migrations on cold start so the DB is always ready
# (SQLite in /tmp — ephemeral but fine for demo)
django.setup()
try:
    from django.core.management import call_command
    call_command('migrate', '--run-syncdb', verbosity=0, interactive=False)
    # Seed demo user if not already present
    from django.contrib.auth.models import User
    if not User.objects.filter(email='demo@example.com').exists():
        User.objects.create_user(
            username='demouser',
            email='demo@example.com',
            password='demo1234',
            first_name='Demo',
            last_name='User',
        )
except Exception:
    pass  # Don't crash if already migrated

app = get_wsgi_application()
