# Generated by Django 5.0.7 on 2024-08-16 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personApp', '0012_police_complaint_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='police_complaint_details',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
