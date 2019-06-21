# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_auto_20170613_1417'),
    ]

    operations = [
        migrations.CreateModel(
            name='AddInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('info', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
