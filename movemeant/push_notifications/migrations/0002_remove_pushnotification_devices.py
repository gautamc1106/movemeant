# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-08-27 22:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('push_notifications', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pushnotification',
            name='devices',
        ),
    ]
