from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from accounts.models import User
from orders.models import Order


class ProfileView(LoginRequiredMixin, View):
    """
    View for displaying user profile
    """
    def get(self, request):
        # Get user's orders
        orders = Order.objects.filter(customer=request.user).order_by('-created_at')[:5]

        context = {
            'user': request.user,
            'orders': orders,
        }
        return render(request, 'profiles/profile_detail.html', context)


class ProfileUpdateView(LoginRequiredMixin, View):
    """
    View for updating user profile
    """
    def get(self, request):
        context = {
            'user': request.user,
        }
        return render(request, 'profiles/profile_edit.html', context)

    def post(self, request):
        user = request.user

        # Update user information
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.address = request.POST.get('address', user.address)

        # Handle password change if provided
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if current_password and new_password1 and new_password2:
            # Create a password change form
            form = PasswordChangeForm(user, {
                'old_password': current_password,
                'new_password1': new_password1,
                'new_password2': new_password2,
            })

            if form.is_valid():
                user = form.save()
                # Update session to prevent logout
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated!')
            else:
                for error in form.errors.values():
                    messages.error(request, error[0])
                return render(request, 'profiles/profile_edit.html', {'user': user})

        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profiles:detail')
