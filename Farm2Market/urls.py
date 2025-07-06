"""
URL configuration for Farm2Market project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from . import test_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
    path('carts/', include('carts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('profiles/', include('profiles.urls')),
    # Test error pages (remove in production)
    path('test-404/', test_views.test_404, name='test_404'),
    path('test-500/', test_views.test_500, name='test_500'),
    path('mpesa/', include('mpesa.urls', namespace='mpesa')),

    # Redirect root URL to products list as a temporary home page
    path('', RedirectView.as_view(pattern_name='products:list'), name='home'),
]

# Custom error handlers
handler404 = 'Farm2Market.error_views.handler404'
handler500 = 'Farm2Market.error_views.handler500'

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
