

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_image'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
            },
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['-created_at'], 'verbose_name': 'Product', 'verbose_name_plural': 'Products'},
        ),
        migrations.AddField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, help_text='Detailed product description'),
        ),
        migrations.AddField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('available', 'Available'), ('out_of_stock', 'Out of Stock'), ('hidden', 'Hidden')], default='available', help_text='Product status', max_length=20),
        ),
        migrations.AddField(
            model_name='product',
            name='stock_quantity',
            field=models.PositiveIntegerField(default=0, help_text='Available quantity in stock'),
        ),
        migrations.AlterField(
            model_name='product',
            name='farmer',
            field=models.ForeignKey(help_text='Farmer who sells this product', limit_choices_to={'role': 'farmer'}, on_delete=django.db.models.deletion.CASCADE, related_name='products', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, help_text='Product image', null=True, upload_to='products/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(help_text='Product name', max_length=100),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, help_text='Product price', max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)]),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(help_text='Product category', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='products.category'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['name'], name='products_pr_name_9ff0a3_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['status'], name='products_pr_status_041708_idx'),
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['price'], name='products_pr_price_9b1a5f_idx'),
        ),
    ]
