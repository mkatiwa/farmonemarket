from django.urls import path
from .views import RegisterView, LoginView, LogoutView, SimpleLoginView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('simple-login/', SimpleLoginView.as_view(), name='simple_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]