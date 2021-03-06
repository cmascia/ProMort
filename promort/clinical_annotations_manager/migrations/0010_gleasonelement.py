# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-14 16:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clinical_annotations_manager', '0009_auto_20170411_0707'),
    ]

    operations = [
        migrations.CreateModel(
            name='GleasonElement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gleason_type', models.CharField(choices=[(b'G1', b'GLEASON_1'), (b'G2', b'GLEASON_2'), (b'G3', b'GLEASON_3'), (b'G4', b'GLEASON_4'), (b'G5', b'GLEASON_5')], max_length=2)),
                ('json_path', models.TextField()),
                ('area', models.FloatField()),
                ('cellular_density_helper_json', models.TextField(blank=True, null=True)),
                ('cellular_density', models.IntegerField(blank=True, null=True)),
                ('cells_count', models.IntegerField(blank=True, null=True)),
                ('focus_region_annotation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                              related_name='gleason_elements',
                                                              to='clinical_annotations_manager.FocusRegionAnnotation')),
            ],
        ),
    ]
