# Generated by Django 4.2.2 on 2023-06-25 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_order_note'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_note',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
    ]
