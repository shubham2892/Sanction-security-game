# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0011_auto_20150910_1736'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='game_key',
            field=models.SlugField(null=True, editable=False, max_length=5, blank=True, unique=True),
        ),
    ]
