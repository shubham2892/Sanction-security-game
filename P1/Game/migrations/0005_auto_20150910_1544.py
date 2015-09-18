# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0004_auto_20150910_1521'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ResearchTask',
            new_name='ResearchObjective',
        ),
        migrations.AlterField(
            model_name='attackresource',
            name='classification',
            field=models.CharField(max_length=10, choices=[(1, b'BLUE'), (2, b'RED'), (3, b'YELLOW')]),
        ),
        migrations.AlterField(
            model_name='player',
            name='email',
            field=models.CharField(default=None, unique=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='researchresource',
            name='classification',
            field=models.CharField(max_length=10, choices=[(1, b'BLUE'), (2, b'RED'), (3, b'YELLOW')]),
        ),
        migrations.AlterField(
            model_name='securityresource',
            name='classification',
            field=models.CharField(max_length=10, choices=[(1, b'BLUE'), (2, b'RED'), (3, b'YELLOW')]),
        ),
        migrations.DeleteModel(
            name='ResourceClassification',
        ),
    ]
