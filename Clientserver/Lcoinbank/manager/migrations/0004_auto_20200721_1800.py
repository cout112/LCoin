# Generated by Django 3.0.7 on 2020-07-21 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0003_auto_20200717_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accounts',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.DeleteModel(
            name='Transactions',
        ),
    ]
