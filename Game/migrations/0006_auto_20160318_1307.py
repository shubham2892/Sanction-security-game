# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0005_auto_20160304_1639'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('n_yellow', models.IntegerField()),
                ('n_red', models.IntegerField()),
                ('n_green', models.IntegerField()),
                ('nf_yellow', models.IntegerField()),
                ('nf_red', models.IntegerField()),
                ('nf_green', models.IntegerField()),
                ('nf_workshop', models.IntegerField()),
                ('nf_conference', models.IntegerField()),
                ('nf_journal', models.IntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='player',
            name='n_sanction',
        ),
        migrations.RemoveField(
            model_name='player',
            name='nf_blue',
        ),
        migrations.RemoveField(
            model_name='player',
            name='nf_conference',
        ),
        migrations.RemoveField(
            model_name='player',
            name='nf_journal',
        ),
        migrations.RemoveField(
            model_name='player',
            name='nf_red',
        ),
        migrations.RemoveField(
            model_name='player',
            name='nf_workshop',
        ),
        migrations.RemoveField(
            model_name='player',
            name='nf_yellow',
        ),
        migrations.AddField(
            model_name='player',
            name='last_manager_sanction',
            field=models.IntegerField(default=-1, editable=False),
        ),
    ]
