# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import Game.custom_models


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0013_remove_tick_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='attack_frequency',
            field=Game.custom_models.IntegerRangeField(default=None),
            preserve_default=False,
        ),
    ]
