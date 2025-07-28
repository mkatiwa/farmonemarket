from django.urls import path
from . import views
from .views import InitiatePaymentView, mpesa_callback, PaymentStatusView



app_name = 'mpesa'
urlpatterns = [
    path('initiate/', InitiatePaymentView.as_view(), name='initiate_payment'),
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
    path('check-status/', PaymentStatusView.as_view(), name='check_status'),
]