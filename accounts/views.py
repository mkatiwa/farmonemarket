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
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'accounts/register.html')

    def post(self, request):
        """Handle POST requests for user registration"""
        data = request.POST
        
        # Get and validate form data
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        password2 = data.get('password2', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        role = data.get('role', '')
        phone = data.get('phone', '').strip()
        address = data.get('address', '').strip()

        # Basic validation
        if not all([email, password, first_name, last_name, role]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'accounts/register.html')

        # Check if passwords match
        if password != password2:
            messages.error(request, 'Passwords do not match. Please try again.')
            return render(request, 'accounts/register.html')

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'accounts/register.html')

        # Validate password
        try:
            validate_password(password)
        except ValidationError as e:
            for error in e:
                messages.error(request, error)
            return render(request, 'accounts/register.html')

        # Validate role
        if role not in ['farmer', 'buyer']:
            messages.error(request, 'Please select a valid role.')
            return render(request, 'accounts/register.html')

        # Create user
        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                phone=phone,
                address=address
            )
            messages.success(request, f'Welcome to Farm2Market, {first_name}! Your account has been created successfully. Please log in.')
            return redirect('accounts:login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}. Please try again.')
            return render(request, 'accounts/register.html')


class LoginView(View):
    """
    View for user login
    """
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'accounts/login.html')

    def post(self, request):
        """Handle POST requests for user login"""
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, 'Please provide both email and password.')
            return render(request, 'accounts/login.html')

        try:
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                if not user.is_active:
                    messages.error(request, 'Your account is not active. Please contact support.')
                    return render(request, 'accounts/login.html')

                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}! Login successful.')
                return redirect('home')
            else:
                messages.error(request, 'Invalid email or password. Please try again.')
                return render(request, 'accounts/login.html')
        except Exception as e:
            messages.error(request, f'Login error: {str(e)}')
            return render(request, 'accounts/login.html')


class SimpleLoginView(View):
    """
    Simple login view for testing
    """
    def get(self, request):
        return render(request, 'accounts/simple_login.html')
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
            return render(request, 'accounts/simple_login.html')


class LogoutView(View):
    """
    View for user logout
    """
    def get(self, request):
        """Handle GET requests for user logout"""
        if request.user.is_authenticated:
            user_name = request.user.first_name or request.user.email
            logout(request)
            messages.success(request, f'Goodbye {user_name}! You have been logged out successfully.')
        return redirect('home')
