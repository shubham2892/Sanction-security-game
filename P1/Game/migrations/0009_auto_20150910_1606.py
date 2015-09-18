# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0008_game_game_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='game_key',
            field=models.CharField(max_length=5, unique=True, null=True, editable=False, blank=True),
        ),
    ]
