# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_remove_create_health_user_password2'),
    ]

    operations = [
        migrations.RenameField(
            model_name='create_health_user',
            old_name='speciality',
            new_name='role',
        ),
    ]
