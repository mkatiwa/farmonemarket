# Generated by Django 5.2.3 on 2025-07-05 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MpesaCallBacks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ip_address', models.TextField()),
                ('caller', models.TextField()),
                ('conversation_id', models.TextField()),
                ('content', models.TextField()),
            ],
            options={
                'verbose_name': 'Mpesa Call Back',
                'verbose_name_plural': 'Mpesa Call Backs',
            },
        ),
        migrations.CreateModel(
            name='MpesaCalls',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('ip_address', models.TextField()),
                ('caller', models.TextField()),
                ('conversation_id', models.TextField()),
                ('content', models.TextField()),
            ],
            options={
                'verbose_name': 'Mpesa Call',
                'verbose_name_plural': 'Mpesa Calls',
            },
        ),
        migrations.CreateModel(
            name='MpesaPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.TextField()),
                ('status', models.CharField(max_length=200)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('phone_number', models.TextField(max_length=13)),
                ('organization_balance', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'verbose_name': 'Mpesa Payment',
                'verbose_name_plural': 'Mpesa Payments',
            },
        ),
    ]
