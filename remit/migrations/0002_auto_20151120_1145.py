# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('remit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('forex_percentage', models.DecimalField(default=4.5, max_digits=10, decimal_places=2)),
                ('transfer_fee_percentage', models.DecimalField(default=4.5, max_digits=10, decimal_places=2)),
                ('transfer_maximum_usd', models.DecimalField(default=500.0, max_digits=10, decimal_places=2)),
                ('transfer_minimum_usd', models.DecimalField(default=100.0, max_digits=10, decimal_places=2)),
                ('mtn_charge', models.DecimalField(default=60.0, max_digits=10, decimal_places=2)),
                ('airtel_charge', models.DecimalField(default=60.0, max_digits=10, decimal_places=2)),
                ('orange_charge', models.DecimalField(default=60.0, max_digits=10, decimal_places=2)),
                ('tigo_charge', models.DecimalField(default=60.0, max_digits=10, decimal_places=2)),
                ('safaricom_charge', models.DecimalField(default=60.0, max_digits=10, decimal_places=2)),
                ('vodafone_charge', models.DecimalField(default=60.0, max_digits=10, decimal_places=2)),
                ('general_network_charge', models.DecimalField(default=60.0, max_digits=10, decimal_places=2)),
                ('added', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('to_usd', models.DecimalField(default=2640.0, max_digits=10, decimal_places=2)),
                ('to_gbp', models.DecimalField(default=3974.0, max_digits=10, decimal_places=2)),
                ('to_eur', models.DecimalField(default=3256.0, max_digits=10, decimal_places=2)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=4)),
                ('name', models.CharField(max_length=40)),
                ('currency', models.CharField(unique=True, max_length=4)),
                ('added', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('dailing_code', models.CharField(default=256, max_length=5)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='charge',
            name='country',
            field=models.ForeignKey(blank=True, to='remit.Country', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='charge',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='country',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='rate',
        ),
        migrations.AddField(
            model_name='transaction',
            name='exchange_rate',
            field=models.DecimalField(default=0.0, max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transaction',
            name='other_fees',
            field=models.DecimalField(default=0.0, max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transaction',
            name='to_country',
            field=models.ForeignKey(related_name=b'target_country', blank=True, to='remit.Country', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='transaction',
            name='added',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
