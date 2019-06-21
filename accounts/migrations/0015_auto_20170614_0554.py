# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0014_create_health_user_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Create_staff_User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=50, blank=True)),
                ('email', models.CharField(max_length=50, blank=True)),
                ('category', models.CharField(max_length=50, blank=True)),
                ('cat_name', models.CharField(max_length=50, blank=True)),
                ('doct_name', models.CharField(max_length=50, blank=True)),
                ('role', models.CharField(max_length=100, blank=True)),
                ('password', models.CharField(max_length=100, blank=True)),
                ('phone', models.CharField(max_length=50, blank=True)),
                ('region', models.CharField(max_length=50, blank=True)),
                ('districts', models.CharField(max_length=50, blank=True)),
                ('info', models.TextField()),
                ('date_joined', models.DateTimeField(default=datetime.datetime.now)),
                ('user', models.OneToOneField(default=b'', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='create_health_user',
            name='user',
        ),
        migrations.DeleteModel(
            name='Create_Health_User',
        ),
    ]
