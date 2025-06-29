from django.contrib import admin
from carts.models import Cart
from . import models


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at' ]
