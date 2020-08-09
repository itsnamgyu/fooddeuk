from django import forms
from django.contrib import admin
from django.utils.html import strip_tags

from .models import *


admin.site.register(Menu)
admin.site.register(ContentSection)
admin.site.register(ContentBlock)
admin.site.register(RichTextBlock)
admin.site.register(ImageBlurb)


class BlurbFilledFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = "Fill Status"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "filled"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (("true", "Filled"), ("false", "Not Filled"))

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == "true":
            return queryset.filter(content__isnull=False)
        if self.value() == "false":
            return queryset.filter(content__isnull=True)


class AdminBlurbForm(forms.ModelForm):
    class Meta:
        model = Blurb
        fields = "__all__"
        fields = ["identifier", "label", "content"]

        widgets = {"label": forms.TextInput()}


@admin.register(Blurb)
class BlurbAdmin(admin.ModelAdmin):
    list_display = ("display_name", "identifier", "preview", "filled")
    list_filter = (BlurbFilledFilter,)
    ordering = ("identifier",)
    form = AdminBlurbForm

    def filled(self, blurb):
        return blurb.content is not None

    def preview(self, blurb):
        return strip_tags(blurb.content)

    filled.boolean = True
