# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-02 22:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ig_miner_app', '0003_auto_20160502_1503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='campaign_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ig_miner_app.Campaign'),
        ),
    ]