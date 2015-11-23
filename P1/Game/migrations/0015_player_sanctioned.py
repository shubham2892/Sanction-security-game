# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0014_game_attack_frequency'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='sanctioned',
            field=models.BooleanField(default=False),
        ),
    ]
