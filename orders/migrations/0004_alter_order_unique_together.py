# Generated by Django 5.1.4 on 2024-12-17 08:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0003_alter_customer_options_alter_customer_email'),
        ('orders', '0003_alter_order_options_order_created_at_order_status_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='order',
            unique_together={('customer', 'robot_serial')},
        ),
    ]
