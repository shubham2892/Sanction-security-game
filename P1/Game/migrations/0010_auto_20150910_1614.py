# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0009_auto_20150910_1606'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='game_key',
            field=models.CharField(unique=True, max_length=5, editable=False, blank=True),
        ),
    ]
