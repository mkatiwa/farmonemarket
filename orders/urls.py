from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='list'),
    path('<uuid:uuid>/', views.OrderDetailView.as_view(), name='detail'),
    path('create/', views.OrderCreateView.as_view(), name='create'),
    path('<uuid:uuid>/update-status/', views.OrderUpdateStatusView.as_view(), name='update_status'),
    path('<uuid:uuid>/delete/', views.OrderDeleteView.as_view(), name='delete'),
]
