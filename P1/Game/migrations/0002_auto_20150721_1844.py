# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourceclassification',
            name='classification',
            field=models.IntegerField(),
        ),
    ]
