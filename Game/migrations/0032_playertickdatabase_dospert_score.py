# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-08 02:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0031_auto_20171114_1823'),
    ]

    operations = [
        migrations.AddField(
            model_name='playertickdatabase',
            name='dospert_score',
            field=models.IntegerField(default=0),
        ),
    ]