from django.core.management.base import BaseCommand, CommandError

from core.models import Photo


class Command(BaseCommand):
    def handle(self, *args, **options):
        count = Photo.objects.all().count()
        if count == 982:
            print("Photos already populated")
            return
        elif count != 0:
            print("Photos already populated.")
            print("Error: {} photo instances exist in DB".format(count))
            return

        photos = []
        for i in range(982):
            photos.append(Photo())
        Photo.objects.bulk_create(photos)
        print("Photos successfully populated.")
