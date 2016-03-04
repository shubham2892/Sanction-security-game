# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Game', '0004_auto_20160304_1638'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='nf_green',
            new_name='nf_blue',
        ),
    ]
