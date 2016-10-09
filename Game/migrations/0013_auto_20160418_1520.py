# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0012_auto_20160418_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='blue_status',
            field=models.BooleanField(default=True, editable=False),
        ),
        migrations.AlterField(
            model_name='player',
            name='red_status',
            field=models.BooleanField(default=True, editable=False),
        ),
        migrations.AlterField(
            model_name='player',
            name='yellow_status',
            field=models.BooleanField(default=True, editable=False),
        ),
    ]
