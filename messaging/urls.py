from django.shortcuts import redirect
from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', lambda request: redirect('messaging:inbox')),
    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent_messages, name='sent_messages'),
    path('send/', views.send_message, name='send_message'),
    path('message/<int:pk>/', views.message_detail, name='message_detail'),
    path('message/<int:pk>/reply/', views.reply_message, name='reply_message'),

]
