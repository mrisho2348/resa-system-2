# Generated by Django 4.2.9 on 2024-03-18 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0023_alter_remotepatientvital_respiratory_rate_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientsurgery',
            name='surgery_date',
            field=models.TextField(blank=True, null=True),
        ),
    ]