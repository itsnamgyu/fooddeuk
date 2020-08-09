"""
This helps you ensure that all of the required environment variables are
defined in the environment (or .env if you use dotenv).

Take a look, it's frickin brilliant.
"""

import os

from django.core.checks import Error, register

missing_required_envs = []


@register()
def check_missing_envs(app_configs, **kwargs):
    errors = []
    for env in missing_required_envs:
        errors.append(
            Error(
                'Required environment variable "{}" missing'.format(env),
                hint="Add this to your .env file",
                obj="settings.py",
            )
        )
    return errors


def require_env(key):
    value = os.environ.get(key, None)
    if not value:
        missing_required_envs.append(key)
    return value


def fetch_env(key, default=None):
    value = os.environ.get(key, default)
    if not value:
        print("Using default value for {:30s} : {}".format(key, value))
    return value
