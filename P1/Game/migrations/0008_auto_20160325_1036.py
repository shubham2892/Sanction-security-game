# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0007_auto_20160325_0239'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='nf_blue',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='player',
            name='nf_conference',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='player',
            name='nf_journal',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='player',
            name='nf_red',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='player',
            name='nf_workshop',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='player',
            name='nf_yellow',
            field=models.IntegerField(default=0, editable=False),
        ),
    ]
