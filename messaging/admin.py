from django.contrib import admin
from messaging import models
from messaging.models import Message


@admin.register(models.Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'subject', 'timestamp', 'is_read']
    list_editable = ['is_read', 'subject']
    list_per_page = 10
    list_display_links = None