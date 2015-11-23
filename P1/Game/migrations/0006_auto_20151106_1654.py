# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0005_auto_20151106_1653'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttackProbability',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('blue', models.IntegerField()),
                ('yellow', models.IntegerField()),
                ('red', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='tick',
            name='next_attack_probability',
            field=models.OneToOneField(default=None, to='Game.AttackProbability'),
            preserve_default=False,
        ),
    ]
