# Generated by Django 4.2.9 on 2024-06-09 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0008_alter_employee_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='GovernmentProgram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('program_name', models.CharField(max_length=100)),
                ('funding_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('eligibility_criteria', models.TextField()),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Grant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grant_name', models.CharField(max_length=100)),
                ('funding_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('donor_name', models.CharField(max_length=100)),
                ('grant_date', models.DateField()),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Investment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('investment_type', models.CharField(max_length=100)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateField()),
                ('description', models.TextField(blank=True)),
            ],
        ),
    ]