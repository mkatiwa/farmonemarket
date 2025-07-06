from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import User

class Category(models.Model):
    """
    Product category model
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Product model representing items that farmers can sell
    """
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock'),
        ('hidden', 'Hidden'),
    )

    name = models.CharField(max_length=100, help_text="Product name")
    description = models.TextField(blank=True, help_text="Detailed product description")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Product price"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='products',
        help_text="Product category"
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Available quantity in stock"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        help_text="Product status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(
        upload_to='products/', 
        null=True, 
        blank=True,
        help_text="Product image"
    )
    farmer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        limit_choices_to={'role': User.Role.FARMER},
        related_name='products',
        help_text="Farmer who sells this product"
    )

    class Meta:
        ordering = ['name']
        # verbose_name = 'Product'
        # verbose_name_plural = 'Products'
        
        # indexes = [
        #     models.Index(fields=['name']),
        #     models.Index(fields=['status']),
        #     models.Index(fields=['price']),
        # ]

    def __str__(self):
        return self.name

    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock_quantity > 0 and self.status == 'available'

    def get_absolute_url(self):
        """Get URL for product's detail view"""
        from django.urls import reverse
        return reverse('products:detail', args=[str(self.id)])
