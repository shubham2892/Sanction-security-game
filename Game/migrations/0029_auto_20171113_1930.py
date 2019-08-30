# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-13 19:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0028_playertickdatabase'),
    ]

    operations = [
        migrations.AddField(
            model_name='playertickdatabase',
            name='number_of_immunities_fixed',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playertickdatabase',
            name='number_of_manager_sanctions',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='playertickdatabase',
            name='number_of_tasks_completed',
            field=models.IntegerField(default=0),
        ),
    ]