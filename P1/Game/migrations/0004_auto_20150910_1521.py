# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0003_auto_20150910_1516'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='user',
        ),
        migrations.AddField(
            model_name='player',
            name='email',
            field=models.CharField(default=None, max_length=50),
        ),
    ]
