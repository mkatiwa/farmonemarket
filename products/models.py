from django.db import models

from accounts.models import User


# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100) # TODO
    created_at =  models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    farmer = models.ForeignKey(User, on_delete=models.CASCADE)


    class Meta:
        ordering = ['-created_at']


    def __str__(self):
        return self.name

    def is_in_stock(self):
        pass # TODO


