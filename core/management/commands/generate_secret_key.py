from django.core.management.base import BaseCommand, CommandError
from django.core.management.utils import get_random_secret_key


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("SECRET_KEY='{}'".format(get_random_secret_key()))
