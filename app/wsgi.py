"""
WSGI config for app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

import dotenv
from django.core.wsgi import get_wsgi_application

# Load environment variables from your .env file. Note that variables that are
# already defined in the environment take precedence over those in your .env file.
# To change this, call read_dotenv(override=True).
dotenv.read_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.base")

application = get_wsgi_application()
