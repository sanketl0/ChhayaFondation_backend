# Generated by Django 5.0.7 on 2024-08-05 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authenticationApp', '0002_alter_customuser_mobile_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='PendingUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('username', models.CharField(max_length=150, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('is_approved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
