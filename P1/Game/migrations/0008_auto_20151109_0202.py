# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0007_auto_20151106_1718'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tick',
            name='attack',
            field=models.OneToOneField(related_name='attack', null=True, default=None, to='Game.AttackResource'),
        ),
    ]
