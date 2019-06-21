# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('remit', '0004_transaction_billtype'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='canceled_by',
            field=models.ForeignKey(related_name=b'admin_canceled', blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transaction',
            name='canceled_on',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transaction',
            name='canceled_reason',
            field=models.CharField(default=False, max_length=230, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transaction',
            name='is_canceled',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
