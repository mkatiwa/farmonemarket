from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Cart, CartItem
from products.models import Product


class CartView(LoginRequiredMixin, View):
    """
    View for displaying the user's shopping cart
    """
    def get(self, request):
        # Get or create cart for the user
        cart, created = Cart.objects.get_or_create(user=request.user)

        context = {
            'cart': cart,
        }
        return render(request, 'carts/cart_detail.html', context)


class AddToCartView(LoginRequiredMixin, View):
    """
    View for adding a product to the cart
    """
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        # Check if product is available
        if product.status != 'available' or product.stock_quantity <= 0:
            messages.error(request, 'This product is not available.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('products:list')))

        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Get quantity from form
        quantity = int(request.POST.get('quantity', 1))

        # Validate quantity
        if quantity <= 0:
            messages.error(request, 'Quantity must be greater than zero.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('products:list')))

        if quantity > product.stock_quantity:
            messages.error(request, f'Only {product.stock_quantity} items available.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('products:list')))

        # Get or create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        # If item already exists, update quantity
        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > product.stock_quantity:
                cart_item.quantity = product.stock_quantity
                messages.warning(request, f'Cart updated to maximum available quantity ({product.stock_quantity}).')
            cart_item.save()

        messages.success(request, f'Added {quantity} x {product.name} to your cart.')
        return redirect('carts:detail')


class RemoveFromCartView(LoginRequiredMixin, View):
    """
    View for removing a product from the cart
    """
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        # Get cart
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.delete()
            messages.success(request, f'Removed {product.name} from your cart.')
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            messages.error(request, 'Item not found in your cart.')

        return redirect('carts:detail')


class UpdateCartView(LoginRequiredMixin, View):
    """
    View for updating the quantity of a product in the cart
    """
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        # Get quantity from form
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            messages.error(request, 'Invalid quantity.')
            return redirect('carts:detail')

        # Validate quantity
        if quantity <= 0:
            return redirect('carts:remove', product_id=product_id)

        if quantity > product.stock_quantity:
            quantity = product.stock_quantity
            messages.warning(request, f'Quantity adjusted to maximum available ({product.stock_quantity}).')

        # Update cart item
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart, product=product)
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, f'Updated {product.name} quantity to {quantity}.')
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            messages.error(request, 'Item not found in your cart.')

        return redirect('carts:detail')


class CheckoutView(LoginRequiredMixin, View):
    """
    View for checkout process
    """
    def get(self, request):
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

            context = {
                'cart': cart,
            }
            return render(request, 'carts/checkout.html', context)

        except Cart.DoesNotExist:
            messages.error(request, 'Your cart is empty.')
            return redirect('carts:detail')


class ClearCartView(LoginRequiredMixin, View):
    """
    View for clearing the cart
    """
    def post(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            messages.success(request, 'Your cart has been cleared.')
        except Cart.DoesNotExist:
            pass

        return redirect('carts:detail')
