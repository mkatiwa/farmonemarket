from django.contrib import admin
from orders.models import Order
from . import models


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_status', 'phone_number', 'customer' ]
    list_editable = ['order_status']
    list_display_links = None