
import django.core.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),

        ('products', '0003_category_alter_product_options_product_description_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(help_text='Name of product at time of order', max_length=100)),
                ('product_price', models.DecimalField(decimal_places=2, help_text='Price of product at time of order', max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('quantity', models.PositiveIntegerField(default=1, help_text='Quantity of product ordered', validators=[django.core.validators.MinValueValidator(1)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Order Item',
                'verbose_name_plural': 'Order Items',
                'ordering': ['created_at'],
            },
        ),
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-created_at'], 'verbose_name': 'Order', 'verbose_name_plural': 'Orders'},
        ),
        migrations.RemoveField(
            model_name='order',
            name='farmer',
        ),
        migrations.RemoveField(
            model_name='order',
            name='products',
        ),
        migrations.AddField(
            model_name='order',
            name='completed_at',
            field=models.DateTimeField(blank=True, help_text='When the order was completed', null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='notes',
            field=models.TextField(blank=True, help_text='Additional notes for the order'),
        ),
        migrations.AddField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled'), ('refunded', 'Refunded')], default='pending', help_text='Current status of the order', max_length=20),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_completed',
            field=models.BooleanField(default=False, help_text='Whether payment has been completed'),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(blank=True, help_text='Method of payment', max_length=50),
        ),
        migrations.AddField(
            model_name='order',
            name='phone_number',
            field=models.CharField(blank=True, help_text='Contact phone number for delivery', max_length=15),
        ),
        migrations.AlterField(
            model_name='order',
            name='customer',
            field=models.ForeignKey(help_text='User who placed the order', on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_address',
            field=models.TextField(help_text='Shipping address for delivery'),
        ),
        migrations.AlterField(
            model_name='order',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier for the order', unique=True),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['uuid'], name='orders_orde_uuid_254377_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['order_status'], name='orders_orde_order_s_33197f_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['customer'], name='orders_orde_custome_59b6fb_idx'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='farmer',
            field=models.ForeignKey(help_text='Farmer who sold this product', limit_choices_to={'role': 'farmer'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sold_items', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(help_text='Order this item belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.order'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(help_text='Product ordered', null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.product'),
        ),
    ]
