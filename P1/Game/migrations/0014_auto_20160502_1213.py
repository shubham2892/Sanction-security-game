# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0013_auto_20160418_1520'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='pass_counter',
        ),
        migrations.RemoveField(
            model_name='player',
            name='pass_total',
        ),
        migrations.AddField(
            model_name='managersanction',
            name='game',
            field=models.ForeignKey(default=None, to='Game.Game'),
        ),
        migrations.AddField(
            model_name='player',
            name='last_tick',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='sanction',
            name='game',
            field=models.ForeignKey(default=None, to='Game.Game'),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='game',
            field=models.ForeignKey(to='Game.Game'),
        ),
    ]
