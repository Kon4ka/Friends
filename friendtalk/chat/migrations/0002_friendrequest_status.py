# Generated by Django 4.2.1 on 2023-05-08 13:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendrequest',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]
