# Generated by Django 5.0.7 on 2024-07-16 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='token',
            field=models.TextField(blank=True, default='0', max_length=256),
        ),
    ]
