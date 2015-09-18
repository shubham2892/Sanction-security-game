# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0007_auto_20150910_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='game_key',
            field=models.CharField(max_length=5, unique=True, null=True, blank=True),
        ),
    ]
