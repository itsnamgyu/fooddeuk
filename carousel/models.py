import os

from django.db import models
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from versatileimagefield.fields import PPOIField, VersatileImageField


class Image(models.Model):
    date_created = models.DateTimeField(_("date created"), auto_now_add=True)
    title = models.CharField(_("title"), max_length=256, null=True, blank=True)
    image = VersatileImageField(
        _("image"),
        upload_to="carousel_image",
        width_field="width",
        height_field="height",
        ppoi_field="ppoi",
    )
    height = models.PositiveIntegerField(_("image height"), blank=True, null=True)
    width = models.PositiveIntegerField(_("image width"), blank=True, null=True)
    ppoi = PPOIField(_("image PPOI"))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def url(self):
        return self.image.url

    def __str__(self):
        if self.title:
            return self.title
        else:
            return os.path.basename(self.image.name)


class Carousel(models.Model):
    date_created = models.DateTimeField(_("date created"), auto_now_add=True)
    identifier = models.CharField(_("identifier"), max_length=256)

    @staticmethod
    def get(identifier):
        """Convenience method"""
        return Carousel.objects.get_or_create(identifier=identifier)

    def empty(self):
        return not self.placements.exists()

    def visible(self):
        return not self.empty()

    def to_html(self):
        if not self.empty():
            context = {"carousel": self}
            rendered = render_to_string("carousel/carousel.html", context=context)
            return mark_safe(rendered)
        else:
            return mark_safe("")

    def __str__(self):
        return self.identifier


class Placement(models.Model):
    date_created = models.DateTimeField(_("date created"), auto_now_add=True)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    carousel = models.ForeignKey(
        Carousel, related_name="placements", on_delete=models.CASCADE
    )
