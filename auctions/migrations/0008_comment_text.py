# Generated by Django 3.2.12 on 2023-07-10 00:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_auto_20230709_0656'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='text',
            field=models.TextField(blank=True),
        ),
    ]
