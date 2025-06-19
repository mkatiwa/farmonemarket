from django.urls import path
from . import views

app_name = 'carts'

urlpatterns = [
    path('', views.CartView.as_view(), name='detail'),
    path('add/<int:product_id>/', views.AddToCartView.as_view(), name='add'),
    path('remove/<int:product_id>/', views.RemoveFromCartView.as_view(), name='remove'),
    path('update/<int:product_id>/', views.UpdateCartView.as_view(), name='update'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('clear/', views.ClearCartView.as_view(), name='clear'),
]
