# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0013_addinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='create_health_user',
            name='user',
            field=models.OneToOneField(default=b'', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
