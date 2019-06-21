# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20170613_1147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='create_health_user',
            name='info',
            field=models.TextField(),
        ),
    ]
