from django.urls import path
from . import views

app_name = 'mpesa'
urlpatterns = [
    path('', views.payment_view, name = 'payment'),
    path('callback/',views.mpesa_callback,name='mpesa_callback'),
    path('stk-status/',views.stk_status_view,name='stk_status_view')
]