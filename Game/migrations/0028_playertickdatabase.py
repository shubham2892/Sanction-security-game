# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-11 20:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0027_auto_20171111_1942'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerTickDatabase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player_username', models.CharField(max_length=100)),
                ('game_key', models.CharField(max_length=100)),
                ('game_type', models.IntegerField(choices=[(1, b'Individual Sanction'), (2, b'Group Sanction'), (0, b'No Sanction')], default=1)),
                ('number_immnunities_fixed_before_deadline', models.IntegerField(default=0)),
            ],
        ),
    ]
