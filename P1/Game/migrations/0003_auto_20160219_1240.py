# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0002_auto_20160218_2335'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='num_of_finished_r_obj',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='player',
            name='num_of_finished_r_task',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='player',
            name='num_of_finished_s_task',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='player',
            name='num_of_santions',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]
