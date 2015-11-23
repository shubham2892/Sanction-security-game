# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0009_auto_20151109_2028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='researchobjective',
            name='research_resources',
            field=models.ForeignKey(blank=True, to='Game.ResearchResource', null=True),
        ),
    ]
