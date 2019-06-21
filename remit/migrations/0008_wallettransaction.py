# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('remit', '0007_transaction_billarea'),
    ]

    operations = [
        migrations.CreateModel(
            name='WalletTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, blank=True)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now, blank=True)),
                ('is_debit', models.BooleanField(default=True)),
                ('amount', models.DecimalField(default=0.0, max_digits=10, decimal_places=2)),
                ('added_by', models.ForeignKey(related_name=b'added_by_who', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(related_name=b'modified_by_who', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('transaction', models.ForeignKey(related_name=b'transaction', to='remit.Transaction')),
                ('wallet', models.ForeignKey(related_name=b'wallet', to='remit.Wallet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
