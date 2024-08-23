# Generated by Django 5.0.7 on 2024-08-07 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('personApp', '0007_alter_multiple_photos_photos'),
    ]

    operations = [
        migrations.AddField(
            model_name='police_station_location',
            name='email',
            field=models.EmailField(blank=True, db_index=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='police_station_location',
            name='phone_number',
            field=models.CharField(blank=True, db_index=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='police_station_location',
            name='website',
            field=models.URLField(blank=True, db_index=True, null=True),
        ),
        migrations.AddIndex(
            model_name='police_station_location',
            index=models.Index(fields=['phone_number', 'email', 'website'], name='personApp_p_phone_n_f812ce_idx'),
        ),
    ]
