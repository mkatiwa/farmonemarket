# Generated by Django 5.2.3 on 2025-06-18 12:52

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('delivery_address', models.CharField(max_length=120)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('farmer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='farmer', to=settings.AUTH_USER_MODEL)),
                ('products', models.ManyToManyField(to='products.product')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
