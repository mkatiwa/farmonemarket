from django.contrib import admin
from products.models import Product
from . import models


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'status' ]
    list_editable = ['price', 'status']
    list_per_page = 10
    list_display_links = None

@admin.display(ordering='status')
def status_status(self, product):
    if product.status < 10:
        return 'Low'
    return 'OK'
