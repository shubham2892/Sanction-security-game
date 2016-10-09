# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0011_auto_20160418_0254'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='blue_status',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='player',
            name='pass_counter',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='player',
            name='pass_total',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='player',
            name='red_status',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='player',
            name='yellow_status',
            field=models.BooleanField(default=True),
        ),
    ]
