# Generated by Django 2.1.7 on 2019-03-28 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('referendum', '0009_referendum_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referendum',
            name='slug',
            field=models.SlugField(blank=True, max_length=300, null=True),
        ),
    ]