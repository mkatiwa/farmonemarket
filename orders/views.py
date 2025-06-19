from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect

from .models import Order, OrderItem
from carts.models import Cart
from products.models import Product


class OrderListView(LoginRequiredMixin, ListView):
    """
    View for displaying a list of user's orders
    """
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying order details
    """
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_queryset(self):
        # Allow farmers to view orders containing their products
        if self.request.user.is_farmer:
            # Get orders that contain products from this farmer
            return Order.objects.filter(items__farmer=self.request.user).distinct()
        # Buyers can only view their own orders
        return Order.objects.filter(customer=self.request.user)


class OrderCreateView(LoginRequiredMixin, View):
    """
    View for creating a new order from the cart
    """
    def post(self, request):
        # Both farmers and buyers can place orders
        # No need to check user role

        # Get cart
        try:
            cart = Cart.objects.get(user=request.user)

            # Check if cart is empty
            if cart.items.count() == 0:
                messages.error(request, 'Your cart is empty.')
                return redirect('carts:detail')

            # Check if all items are still available
            for item in cart.items.all():
                if item.product.status != 'available' or item.product.stock_quantity < item.quantity:
                    messages.error(request, f'{item.product.name} is no longer available in the requested quantity.')
                    return redirect('carts:detail')

            # Create order
            order = Order.objects.create(
                customer=request.user,
                delivery_address=request.POST.get('delivery_address', request.user.address),
                phone_number=request.POST.get('phone_number', request.user.phone),
                notes=request.POST.get('notes', ''),
                payment_method=request.POST.get('payment_method', 'cash_on_delivery')
            )

            # Create order items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity
                )

                # Update product stock
                product = cart_item.product
                product.stock_quantity -= cart_item.quantity
                if product.stock_quantity <= 0:
                    product.status = 'out_of_stock'
                product.save()

            # Clear cart
            cart.items.all().delete()

            messages.success(request, f'Order #{order.uuid} placed successfully!')
            return redirect('orders:detail', uuid=order.uuid)

        except Cart.DoesNotExist:
            messages.error(request, 'Your cart is empty.')
            return redirect('carts:detail')


class OrderUpdateStatusView(LoginRequiredMixin, View):
    """
    View for updating order status
    """
    def post(self, request, uuid):
        order = get_object_or_404(Order, uuid=uuid)

        # Check permissions
        if not (request.user.is_staff or request.user == order.customer or 
                order.items.filter(farmer=request.user).exists()):
            messages.error(request, 'You do not have permission to update this order.')
            return redirect('orders:list')

        # Update status
        new_status = request.POST.get('order_status')
        if new_status in dict(Order.Status.choices):
            old_status = order.order_status
            order.order_status = new_status

            # If order is marked as delivered, set completed_at
            if new_status == Order.Status.DELIVERED and old_status != Order.Status.DELIVERED:
                order.completed_at = timezone.now()

            # If order is marked as paid, set payment_completed
            if new_status == Order.Status.PAID:
                order.payment_completed = True

            order.save()
            messages.success(request, f'Order status updated to {order.get_order_status_display()}.')
        else:
            messages.error(request, 'Invalid status.')

        return redirect('orders:detail', uuid=order.uuid)


class OrderDeleteView(LoginRequiredMixin, View):
    """
    View for deleting an order
    """
    def post(self, request, uuid):
        order = get_object_or_404(Order, uuid=uuid)

        # Only staff or the customer can delete an order
        if not (request.user.is_staff or request.user == order.customer):
            messages.error(request, 'You do not have permission to delete this order.')
            return redirect('orders:list')

        # Can only delete pending orders
        if order.order_status != Order.Status.PENDING:
            messages.error(request, 'Only pending orders can be deleted.')
            return redirect('orders:detail', uuid=order.uuid)

        # Return items to stock
        for item in order.items.all():
            if item.product:
                product = item.product
                product.stock_quantity += item.quantity
                if product.status == 'out_of_stock' and product.stock_quantity > 0:
                    product.status = 'available'
                product.save()

        order.delete()
        messages.success(request, 'Order deleted successfully.')
        return redirect('orders:list')
