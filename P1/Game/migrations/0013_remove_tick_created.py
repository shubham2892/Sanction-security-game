# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0012_tick_created'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tick',
            name='created',
        ),
    ]
