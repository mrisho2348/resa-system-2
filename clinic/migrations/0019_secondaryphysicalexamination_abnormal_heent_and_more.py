# Generated by Django 4.2.9 on 2024-12-28 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0018_remove_imagingrecord_total_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='secondaryphysicalexamination',
            name='abnormal_heent',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='secondaryphysicalexamination',
            name='normal_heent',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
