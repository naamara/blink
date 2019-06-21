# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20160829_2125'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='id_pic',
            field=models.ImageField(upload_to=b'images/uploads/', blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='profile_pic',
            field=models.ImageField(upload_to=b'images/images/thumbs/', blank=True),
        ),
    ]
