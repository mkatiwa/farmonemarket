from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from products.models import Product

class Cart(models.Model):
    """
    Shopping cart model to store items before checkout
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='cart',
        help_text="User who owns this cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['-created_at']

    def __str__(self):
        return f"Cart for {self.user.email}"

    @property
    def total_price(self):
        """Calculate total price of all items in cart"""
        return sum(item.total_price for item in self.items.all())

    @property
    def item_count(self):
        """Count total number of items in cart"""
        return self.items.count()

class CartItem(models.Model):
    """
    Individual item in a shopping cart
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Cart this item belongs to"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        help_text="Product in cart"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantity of product"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        ordering = ['-created_at']
        unique_together = ['cart', 'product']  # Prevent duplicate products in cart

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart for {self.cart.user.email}"

    @property
    def total_price(self):
        """Calculate total price for this item (quantity * price)"""
        return self.quantity * self.product.price
