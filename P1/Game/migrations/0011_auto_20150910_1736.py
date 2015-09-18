# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0010_auto_20150910_1614'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attackdeck',
            name='attack_resources',
        ),
        migrations.RemoveField(
            model_name='attackresource',
            name='description',
        ),
        migrations.RemoveField(
            model_name='game',
            name='deck',
        ),
        migrations.RemoveField(
            model_name='researchresource',
            name='description',
        ),
        migrations.RemoveField(
            model_name='securityresource',
            name='description',
        ),
        migrations.AddField(
            model_name='player',
            name='first_name',
            field=models.CharField(default=None, max_length=50),
        ),
        migrations.AddField(
            model_name='player',
            name='last_name',
            field=models.CharField(default=None, max_length=50),
        ),
        migrations.AddField(
            model_name='researchobjective',
            name='name',
            field=models.IntegerField(default=None, choices=[(1, b'Workshop'), (2, b'Conference'), (3, b'Journal')]),
        ),
        migrations.AlterField(
            model_name='game',
            name='game_key',
            field=models.CharField(max_length=5, unique=True, null=True, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='researchobjective',
            name='deadline',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='researchobjective',
            name='value',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.DeleteModel(
            name='AttackDeck',
        ),
    ]
