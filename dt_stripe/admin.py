from django.contrib import admin

from .models import *

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(SKU)
admin.site.register(Plan)
admin.site.register(Subscription)
