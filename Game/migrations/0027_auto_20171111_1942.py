# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-11 19:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0026_playertickdup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conference',
            name='score',
            field=models.IntegerField(default=25),
        ),
    ]