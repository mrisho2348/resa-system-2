# Generated by Django 4.2.9 on 2024-06-08 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0005_alter_bankaccount_bank_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentmethod',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]