# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0009_auto_20160330_1447'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='last_manager_sanction',
        ),
        migrations.AddField(
            model_name='player',
            name='last_tick_blue',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='player',
            name='last_tick_red',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='player',
            name='last_tick_yellow',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]
