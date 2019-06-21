# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('remit', '0005_auto_20151203_0957'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('balance', models.DecimalField(default=0.0, max_digits=10, decimal_places=2)),
                ('currency', models.CharField(default=b'USD', max_length=4, blank=True)),
                ('credit', models.DecimalField(default=0.0, max_digits=10, decimal_places=2)),
                ('debit', models.DecimalField(default=0.0, max_digits=10, decimal_places=2)),
                ('added', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, blank=True)),
                ('modified_by', models.ForeignKey(related_name=b'modified_by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='transaction',
            name='from_wallet',
            field=models.ForeignKey(related_name=b'Wallet', blank=True, to='remit.Wallet', null=True),
            preserve_default=True,
        ),
    ]
