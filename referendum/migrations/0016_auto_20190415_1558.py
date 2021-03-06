# Generated by Django 2.2 on 2019-04-15 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('referendum', '0015_auto_20190411_1533'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='choice',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='choice',
            constraint=models.UniqueConstraint(fields=('title', 'referendum'), name='unique_choice'),
        ),
    ]
