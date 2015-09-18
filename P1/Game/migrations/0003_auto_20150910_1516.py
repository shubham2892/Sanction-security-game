# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0002_auto_20150721_1844'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='player',
            options={},
        ),
        migrations.RenameField(
            model_name='game',
            old_name='rounds',
            new_name='ticks',
        ),
        migrations.RemoveField(
            model_name='attackresource',
            name='name',
        ),
        migrations.RemoveField(
            model_name='game',
            name='duration',
        ),
        migrations.RemoveField(
            model_name='game',
            name='game_key',
        ),
        migrations.RemoveField(
            model_name='researchresource',
            name='name',
        ),
        migrations.RemoveField(
            model_name='researchtask',
            name='name',
        ),
        migrations.RemoveField(
            model_name='securityresource',
            name='name',
        ),
    ]
