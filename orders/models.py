from django.db import models
import uuid
from django.core.validators import MinValueValidator
from accounts.models import User
from products.models import Product

class Order(models.Model):
    """
    Order model to track customer purchases
    """
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'
        REFUNDED = 'refunded', 'Refunded'

    uuid = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True,
        help_text="Unique identifier for the order"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='orders',
        help_text="User who placed the order"
    )
    order_status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING,
        help_text="Current status of the order"
    )
    delivery_address = models.TextField(
        help_text="Shipping address for delivery"
    )
    phone_number = models.CharField(
        max_length=15, 
        blank=True,
        help_text="Contact phone number for delivery"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes for the order"
    )
    payment_method = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Method of payment"
    )
    payment_completed = models.BooleanField(
        default=False,
        help_text="Whether payment has been completed"
    )
    completed_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When the order was completed"
    )

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['uuid']),
            models.Index(fields=['order_status']),
            models.Index(fields=['customer']),
        ]

    def __str__(self):
        return f"Order {self.uuid} ({self.get_order_status_display()})"

    @property
    def total_price(self):
        """Calculate total price of all items in order"""
        return sum(item.total_price for item in self.items.all())

    @property
    def item_count(self):
        """Count total number of items in order"""
        return self.items.count()

class OrderItem(models.Model):
    """
    Individual item in an order
    """
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Order this item belongs to"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL,
        null=True,
        help_text="Product ordered"
    )
    farmer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sold_items',
        limit_choices_to={'role': User.Role.FARMER},
        help_text="Farmer who sold this product"
    )
    product_name = models.CharField(
        max_length=100,
        help_text="Name of product at time of order"
    )
    product_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Price of product at time of order"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantity of product ordered"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.quantity} x {self.product_name} in order {self.order.uuid}"

    @property
    def total_price(self):
        """Calculate total price for this item (quantity * price)"""
        return self.quantity * self.product_price

    def save(self, *args, **kwargs):
        """
        Override save to store product details at time of order
        """
        if self.product and not self.id:  # Only on creation
            self.product_name = self.product.name
            self.product_price = self.product.price
            self.farmer = self.product.farmer
        super().save(*args, **kwargs)
