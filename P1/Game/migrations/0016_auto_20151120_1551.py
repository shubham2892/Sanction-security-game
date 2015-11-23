# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0015_player_sanctioned'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='complete',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='player',
            name='sanctioned',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
