# Generated by Django 4.2.9 on 2025-07-03 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0030_remoteimagingrecord_remove_remotecompany_founded_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='remoteprescription',
            name='issued',
        ),
        migrations.RemoveField(
            model_name='remoteprescription',
            name='status',
        ),
        migrations.RemoveField(
            model_name='remoteprescription',
            name='total_price',
        ),
        migrations.RemoveField(
            model_name='remoteprescription',
            name='verified',
        ),
        migrations.AddField(
            model_name='remoteconsultationnotes',
            name='pathology',
            field=models.ManyToManyField(blank=True, to='clinic.pathodologyrecord'),
        ),
    ]
