from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard views
    path('farmer/', views.FarmerDashboardView.as_view(), name='farmer'),
    path('buyer/', views.BuyerDashboardView.as_view(), name='buyer'),

    # Farmer product management
    path('farmer/products/', views.FarmerProductsView.as_view(), name='farmer_products'),

    # Farmer order management
    path('farmer/orders/', views.FarmerOrdersView.as_view(), name='farmer_orders'),

    # Farmer analytics
    path('farmer/analytics/', views.FarmerAnalyticsView.as_view(), name='farmer_analytics'),

    # Farmer inventory management
    path('farmer/inventory/', views.FarmerInventoryView.as_view(), name='farmer_inventory'),
    path('farmer/inventory/update/<int:product_id>/', views.UpdateInventoryView.as_view(), name='update_inventory'),
]
