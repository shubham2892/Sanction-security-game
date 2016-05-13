# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0014_auto_20160502_1213'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='last_tick',
        ),
        migrations.AddField(
            model_name='player',
            name='counter',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='player',
            name='counter_sum',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]
