# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0006_auto_20160318_1307'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statistics',
            name='n_green',
        ),
        migrations.RemoveField(
            model_name='statistics',
            name='n_red',
        ),
        migrations.RemoveField(
            model_name='statistics',
            name='n_yellow',
        ),
        migrations.RemoveField(
            model_name='statistics',
            name='nf_conference',
        ),
        migrations.RemoveField(
            model_name='statistics',
            name='nf_green',
        ),
        migrations.RemoveField(
            model_name='statistics',
            name='nf_journal',
        ),
        migrations.RemoveField(
            model_name='statistics',
            name='nf_red',
        ),
        migrations.RemoveField(
            model_name='statistics',
            name='nf_workshop',
        ),
        migrations.RemoveField(
            model_name='statistics',
            name='nf_yellow',
        ),
        migrations.AddField(
            model_name='statistics',
            name='stat_number',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='statistics',
            name='stat_tick',
            field=models.ForeignKey(to='Game.Tick', null=True),
        ),
        migrations.AddField(
            model_name='statistics',
            name='type_of_task',
            field=models.IntegerField(default=None, choices=[(0, b'Workshop Research Task'), (1, b'Conference Research Task'), (2, b'Journal Research Task'), (3, b'Red Security Task'), (4, b'Yellow Security Task'), (5, b'Blue Security Task')]),
        ),
    ]
