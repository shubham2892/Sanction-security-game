# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='manager_sanc',
            field=models.IntegerField(default=1, choices=[(1, b'Individual Sanction'), (2, b'Group Sanction'), (0, b'No Sanction')]),
        ),
        migrations.AddField(
            model_name='game',
            name='peer_sanc',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='message',
            name='tick',
            field=models.ForeignKey(editable=False, to='Game.Tick', null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='props',
            field=models.IntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='playertick',
            name='action',
            field=models.IntegerField(default=0, choices=[(0, b'The player did not move.'), (1, b'sanctioned player'), (2, b'activated security resource'), (3, b'completed research task'), (4, b'completed research objective')]),
        ),
        migrations.AlterField(
            model_name='attackresource',
            name='classification',
            field=models.IntegerField(choices=[(1, b'blue'), (2, b'red'), (3, b'yellow'), (4, b'lab')]),
        ),
        migrations.AlterField(
            model_name='researchresource',
            name='classification',
            field=models.IntegerField(blank=True, null=True, choices=[(1, b'blue'), (2, b'red'), (3, b'yellow'), (4, b'lab')]),
        ),
        migrations.AlterField(
            model_name='securityresource',
            name='classification',
            field=models.IntegerField(choices=[(1, b'blue'), (2, b'red'), (3, b'yellow'), (4, b'lab')]),
        ),
    ]
