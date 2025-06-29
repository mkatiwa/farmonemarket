from django.contrib import admin
from . import models
from accounts.models import User

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'role', 'phone']
    list_editable = ['role', 'email', 'phone' ]
    list_display_links = None