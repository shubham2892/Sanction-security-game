# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0008_auto_20160325_1036'),
    ]

    operations = [
        migrations.RenameField(
            model_name='statistics',
            old_name='stat_number',
            new_name='nf_finished_task',
        ),
        migrations.RemoveField(
            model_name='statistics',
            name='stat_tick',
        ),
        migrations.AddField(
            model_name='statistics',
            name='game',
            field=models.ForeignKey(default=None, to='Game.Game'),
        ),
        migrations.AddField(
            model_name='statistics',
            name='player',
            field=models.ForeignKey(default=None, to='Game.Player'),
        ),
        migrations.AddField(
            model_name='statistics',
            name='player_tick',
            field=models.ForeignKey(default=None, to='Game.PlayerTick'),
        ),
    ]
