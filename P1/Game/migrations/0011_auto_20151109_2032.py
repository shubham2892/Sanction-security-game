# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0010_auto_20151109_2030'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='researchobjective',
            name='research_resources',
        ),
        migrations.AddField(
            model_name='researchobjective',
            name='research_resources',
            field=models.ManyToManyField(to='Game.ResearchResource'),
        ),
    ]
