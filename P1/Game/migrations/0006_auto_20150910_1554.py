# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0005_auto_20150910_1544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attackresource',
            name='classification',
            field=models.IntegerField(choices=[(1, b'BLUE'), (2, b'RED'), (3, b'YELLOW')]),
        ),
        migrations.AlterField(
            model_name='game',
            name='deck',
            field=models.ForeignKey(to='Game.AttackDeck', null=True),
        ),
        migrations.AlterField(
            model_name='researchresource',
            name='classification',
            field=models.IntegerField(choices=[(1, b'BLUE'), (2, b'RED'), (3, b'YELLOW')]),
        ),
        migrations.AlterField(
            model_name='securityresource',
            name='classification',
            field=models.IntegerField(choices=[(1, b'BLUE'), (2, b'RED'), (3, b'YELLOW')]),
        ),
    ]
