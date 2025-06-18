from django.db import models
import uuid

from accounts.models import User
from products.models import Product


# Create your models here.

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending'
        PAID = 'paid'

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE) #TODO
    farmer = models.ForeignKey(User, on_delete= models.CASCADE, related_name='farmer')
    products = models.ManyToManyField(Product) # TODO
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    delivery_address = models.CharField(max_length=120)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)



    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"order {self.uuid}"

    @property
    def status(self):
        pass

