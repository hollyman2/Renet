# Generated by Django 5.0.2 on 2024-02-21 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Account', '0004_follower'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='username',
            field=models.CharField(max_length=50, unique=True, verbose_name='username'),
        ),
    ]
