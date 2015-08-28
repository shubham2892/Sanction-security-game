# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AttackDeck',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='AttackResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=25)),
                ('description', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rounds', models.IntegerField()),
                ('duration', models.DurationField(default=datetime.timedelta(0, 3600))),
                ('game_key', models.CharField(max_length=15)),
                ('deck', models.ForeignKey(to='Game.AttackDeck')),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Players',
            },
        ),
        migrations.CreateModel(
            name='ResearchResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=25)),
                ('description', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='ResearchTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=25)),
                ('value', models.IntegerField()),
                ('deadline', models.IntegerField()),
                ('required_resources', models.ManyToManyField(to='Game.ResearchResource')),
            ],
        ),
        migrations.CreateModel(
            name='ResourceClassification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('classification', models.IntegerField(max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='SecurityResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=25)),
                ('description', models.CharField(max_length=150)),
                ('classification', models.ForeignKey(to='Game.ResourceClassification')),
            ],
        ),
        migrations.AddField(
            model_name='researchresource',
            name='classification',
            field=models.ForeignKey(to='Game.ResourceClassification'),
        ),
        migrations.AddField(
            model_name='game',
            name='players',
            field=models.ManyToManyField(to='Game.Player'),
        ),
        migrations.AddField(
            model_name='attackresource',
            name='classification',
            field=models.ForeignKey(to='Game.ResourceClassification'),
        ),
        migrations.AddField(
            model_name='attackdeck',
            name='attack_resources',
            field=models.ManyToManyField(to='Game.AttackResource'),
        ),
    ]
