from django.contrib import admin
from django.http import HttpResponseRedirect


class ModelAdmin(admin.ModelAdmin):
    """Use this ModelAdmin to enable URL redirects for admin screens.

    E.g.
    <a href="{% url 'myapp_mymodel_add' %}?admin_link_redirect={{ path }}">
    """

    def _response_post_save(self, request, obj):
        redirect = request.GET.get("admin_link_redirect")
        if redirect:
            return HttpResponseRedirect(redirect)
        else:
            return super(ModelAdmin, self)._response_post_save(request, obj)
