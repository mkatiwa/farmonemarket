from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from products.models import Product

User = get_user_model()

# Create your views here.

class RegisterView(View):
    """
    View for user registration
    """
    def get(self, request):
        return render(request, 'accounts/register.html')

    def post(self, request):
        data = request.POST

        # Check if passwords match
        if data.get('password') != data.get('password2'):
            raise ValidationError('Passwords must match')
            messages.error(request, 'Passwords do not match')
            return render(request, 'accounts/register.html')

        # Validate password
        try:
            validate_password(data.get('password'))
        except ValidationError as e:
            for error in e:
                messages.error(request, error)
            return render(request, 'accounts/register.html')

        # Create user
        try:
            user = User.objects.create_user(
                email=data.get('email'),
                password=data.get('password'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                role=data.get('role'),
                phone=data.get('phone', ''),
                address=data.get('address', '')
            )
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('accounts:login')
        except Exception as e:
            raise e
            messages.error(request, str(e))
            return render(request, 'accounts/register.html')


class LoginView(View):
    """
    View for user login
    """
    def get(self, request):
        return render(request, 'accounts/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            # TODO activate user
            login(request, user)
            messages.success(request, 'Login successful')

            # Redirect based on user role
            if user.is_farmer:
                products = Product.objects.filter(user=user)
                context = {
                    "products": products,
                }
                return render(request, 'products/seller_product_list.html', context= context) #
            else:
                products = Product.objects.all()
                context = {
                    "products": products,
                }
                return render(request, 'products/product_list.html', context= context)
        else:
            messages.error(request, 'Invalid email or password')
            return render(request, 'accounts/login.html')


class LogoutView(View):
    """
    View for user logout
    """
    def get(self, request):
        logout(request)
        messages.success(request, 'Logout successful')
        return redirect('login')
