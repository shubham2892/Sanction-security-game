# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0002_remove_player_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='number',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]
