"""
Django settings configuration for pytest.
This ensures Django is properly configured before tests run.
"""
import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django
if not settings.configured:
    django.setup()
