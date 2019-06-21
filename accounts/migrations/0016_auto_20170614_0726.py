# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_auto_20170614_0554'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminprofile',
            name='is_doctor',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='adminprofile',
            name='is_educ',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='adminprofile',
            name='is_jounalist',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='adminprofile',
            name='is_lawyer',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
