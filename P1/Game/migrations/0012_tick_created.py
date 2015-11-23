# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0011_auto_20151109_2032'),
    ]

    operations = [
        migrations.AddField(
            model_name='tick',
            name='created',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
