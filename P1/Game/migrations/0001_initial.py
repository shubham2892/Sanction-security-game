# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import Game.custom_models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AttackProbability',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('blue', models.IntegerField()),
                ('yellow', models.IntegerField()),
                ('red', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='AttackResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('classification', models.IntegerField(choices=[(1, b'blue'), (2, b'red'), (3, b'yellow')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Capabilities',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_ticks', models.IntegerField()),
                ('game_key', models.CharField(max_length=10, unique=True, null=True, editable=False, blank=True)),
                ('attack_frequency', Game.custom_models.IntegerRangeField()),
                ('complete', models.BooleanField(default=False, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(max_length=500, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.IntegerField(default=0, editable=False)),
                ('number', models.IntegerField(default=0, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('game', models.ForeignKey(to='Game.Game')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PlayerTick',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('player', models.ForeignKey(to='Game.Player')),
            ],
        ),
        migrations.CreateModel(
            name='ResearchObjective',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.IntegerField(default=None, choices=[(1, b'workshop'), (2, b'conference'), (3, b'journal')])),
                ('value', models.IntegerField(null=True, blank=True)),
                ('deadline', models.IntegerField(null=True, blank=True)),
                ('complete', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('player', models.ForeignKey(to='Game.Player')),
            ],
        ),
        migrations.CreateModel(
            name='ResearchResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('classification', models.IntegerField(blank=True, null=True, choices=[(1, b'blue'), (2, b'red'), (3, b'yellow')])),
                ('complete', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sanction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tick_number', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('sanctionee', models.ForeignKey(related_name='sanctionee', to='Game.Player')),
                ('sanctioner', models.ForeignKey(related_name='sanctioner', to='Game.Player')),
            ],
        ),
        migrations.CreateModel(
            name='SecurityResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('classification', models.IntegerField(choices=[(1, b'blue'), (2, b'red'), (3, b'yellow')])),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tick',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField(default=1)),
                ('complete', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('attack', models.OneToOneField(related_name='attack', null=True, default=None, to='Game.AttackResource')),
                ('game', models.ForeignKey(to='Game.Game')),
                ('next_attack_probability', models.OneToOneField(to='Game.AttackProbability')),
            ],
        ),
        migrations.CreateModel(
            name='Vulnerabilities',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('player', models.OneToOneField(null=True, to='Game.Player')),
                ('security_resources', models.ManyToManyField(to='Game.SecurityResource')),
            ],
        ),
        migrations.AddField(
            model_name='researchobjective',
            name='research_resources',
            field=models.ManyToManyField(to='Game.ResearchResource'),
        ),
        migrations.AddField(
            model_name='playertick',
            name='tick',
            field=models.ForeignKey(to='Game.Tick'),
        ),
        migrations.AddField(
            model_name='message',
            name='created_by',
            field=models.ForeignKey(editable=False, to='Game.Player', null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='game',
            field=models.ForeignKey(editable=False, to='Game.Game', null=True),
        ),
        migrations.AddField(
            model_name='capabilities',
            name='player',
            field=models.OneToOneField(null=True, to='Game.Player'),
        ),
        migrations.AddField(
            model_name='capabilities',
            name='security_resources',
            field=models.ManyToManyField(to='Game.SecurityResource'),
        ),
    ]
