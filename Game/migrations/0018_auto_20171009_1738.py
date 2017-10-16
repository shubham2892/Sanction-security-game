# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-09 17:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0017_gamesets_chat_link'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='capabilities',
            name='player',
        ),
        migrations.RemoveField(
            model_name='capabilities',
            name='security_resources',
        ),
        migrations.RemoveField(
            model_name='vulnerabilities',
            name='player',
        ),
        migrations.RemoveField(
            model_name='vulnerabilities',
            name='security_resources',
        ),
        migrations.RenameField(
            model_name='player',
            old_name='blue_status',
            new_name='blue_status_capability',
        ),
        migrations.RenameField(
            model_name='player',
            old_name='red_status',
            new_name='blue_status_security',
        ),
        migrations.RenameField(
            model_name='player',
            old_name='yellow_status',
            new_name='red_status_capability',
        ),
        migrations.RemoveField(
            model_name='player',
            name='counter',
        ),
        migrations.RemoveField(
            model_name='player',
            name='counter_sum',
        ),
        migrations.RemoveField(
            model_name='player',
            name='props',
        ),
        migrations.AddField(
            model_name='attackprobability',
            name='lab',
            field=models.IntegerField(default=12),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='player',
            name='red_status_security',
            field=models.BooleanField(default=True, editable=False),
        ),
        migrations.AddField(
            model_name='player',
            name='yellow_status_capability',
            field=models.BooleanField(default=True, editable=False),
        ),
        migrations.AddField(
            model_name='player',
            name='yellow_status_security',
            field=models.BooleanField(default=True, editable=False),
        ),
        migrations.DeleteModel(
            name='Capabilities',
        ),
        migrations.DeleteModel(
            name='SecurityResource',
        ),
        migrations.DeleteModel(
            name='Vulnerabilities',
        ),
    ]