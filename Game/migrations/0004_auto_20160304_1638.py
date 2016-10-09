# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0003_auto_20160219_1240'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManagerSanction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tick_number', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RenameField(
            model_name='player',
            old_name='num_of_finished_r_obj',
            new_name='n_sanction',
        ),
        migrations.RenameField(
            model_name='player',
            old_name='num_of_finished_r_task',
            new_name='nf_conference',
        ),
        migrations.RenameField(
            model_name='player',
            old_name='num_of_finished_s_task',
            new_name='nf_green',
        ),
        migrations.RenameField(
            model_name='player',
            old_name='num_of_santions',
            new_name='nf_journal',
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
        migrations.AddField(
            model_name='managersanction',
            name='sanctionee',
            field=models.ForeignKey(related_name='sanctionee_by_manager', to='Game.Player'),
        ),
    ]
