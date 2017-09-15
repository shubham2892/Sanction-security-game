# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Game', '0015_auto_20160512_1938'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameSets',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('consent_check', models.BooleanField(default=False)),
                ('video_check', models.BooleanField(default=False)),
                ('demo_check', models.BooleanField(default=False)),
                ('g1_check', models.BooleanField(default=False)),
                ('g2_check', models.BooleanField(default=False)),
                ('g3_check', models.BooleanField(default=False)),
                ('demo_id', models.ForeignKey(related_name='game_demo', to='Game.Game')),
                ('game_id1', models.ForeignKey(related_name='game_id1', to='Game.Game')),
                ('game_id2', models.ForeignKey(related_name='game_id2', to='Game.Game')),
                ('game_id3', models.ForeignKey(related_name='game_id3', to='Game.Game')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
