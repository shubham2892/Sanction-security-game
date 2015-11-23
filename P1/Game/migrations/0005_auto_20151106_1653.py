# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0004_auto_20151106_1652'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tick',
            name='next_attack_probability',
        ),
        migrations.DeleteModel(
            name='AttackProbability',
        ),
    ]
