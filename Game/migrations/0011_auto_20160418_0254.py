# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0010_auto_20160401_0244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playertick',
            name='action',
            field=models.IntegerField(default=0, choices=[(0, b'The player did not move.'), (1, b'sanctioned player'), (2, b'activated security resource'), (3, b'completed research task'), (4, b'completed research objective'), (5, b'clicked the pass button')]),
        ),
    ]
