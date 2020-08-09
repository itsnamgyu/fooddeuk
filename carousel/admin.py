from django.contrib import admin
from django.forms import ModelForm

from versatileimagefield.fields import SizedImageCenterpointClickDjangoAdminField
from versatileimagefield.widgets import VersatileImagePPOIClickWidget
from versatileimagefield.fields import VersatileImageField

from admin_link.admin import ModelAdmin

from .models import Carousel, Image, Placement


@admin.register(Image)
class ImageAdmin(ModelAdmin):
    list_display = ["title", "image"]
    empty_value_display = "unset"

    def name(self, image):
        return str(image)


# Register your models here.
class PlacementInline(admin.TabularInline):
    model = Placement


@admin.register(Carousel)
class CarouselAdmin(ModelAdmin):
    inlines = [PlacementInline]
    list_display = ["identifier", "date_created", "image_count"]

    def image_count(self, carousel):
        return carousel.placements.count()

