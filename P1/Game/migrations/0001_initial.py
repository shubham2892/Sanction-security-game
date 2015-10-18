# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AttackResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('classification', models.IntegerField(choices=[(1, b'BLUE'), (2, b'RED'), (3, b'YELLOW')])),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ticks', models.IntegerField()),
                ('game_key', models.CharField(max_length=5, unique=True, null=True, editable=False, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ResearchObjective',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.IntegerField(default=None, choices=[(1, b'Workshop'), (2, b'Conference'), (3, b'Journal')])),
                ('value', models.IntegerField(null=True, blank=True)),
                ('deadline', models.IntegerField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ResearchResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('classification', models.IntegerField(choices=[(1, b'BLUE'), (2, b'RED'), (3, b'YELLOW')])),
            ],
        ),
        migrations.CreateModel(
            name='SecurityResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('classification', models.IntegerField(choices=[(1, b'BLUE'), (2, b'RED'), (3, b'YELLOW')])),
            ],
        ),
        migrations.AddField(
            model_name='researchobjective',
            name='required_resources',
            field=models.ManyToManyField(to='Game.ResearchResource'),
        ),
        migrations.AddField(
            model_name='game',
            name='players',
            field=models.ManyToManyField(to='Game.Player'),
        ),
    ]
