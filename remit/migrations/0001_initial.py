# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import remit.models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Phonebook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ext', models.IntegerField()),
                ('number', models.IntegerField()),
                ('country_code', models.CharField(default=b'256', max_length=3)),
                ('firstname', models.TextField()),
                ('lastname', models.TextField(default=False, blank=True)),
                ('added', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('usd_to_rwf', models.DecimalField(default=688.0, max_digits=10, decimal_places=2)),
                ('gbp_to_rwf', models.DecimalField(default=1114.76, max_digits=10, decimal_places=2)),
                ('usd_to_ugx', models.DecimalField(default=2640.0, max_digits=10, decimal_places=2)),
                ('usd_to_kes', models.DecimalField(default=85.63, max_digits=10, decimal_places=2)),
                ('usd_to_tzs', models.DecimalField(default=1623.0, max_digits=10, decimal_places=2)),
                ('gbp_to_ugx', models.DecimalField(default=3974.19, max_digits=10, decimal_places=2)),
                ('gpb_to_kes', models.DecimalField(default=129.47, max_digits=10, decimal_places=2)),
                ('gpb_to_tzs', models.DecimalField(default=2453.0, max_digits=10, decimal_places=2)),
                ('transfer_limit_usd', models.DecimalField(default=500.0, max_digits=10, decimal_places=2)),
                ('transfer_minimum_usd', models.DecimalField(default=100.0, max_digits=10, decimal_places=2)),
                ('our_percentage', models.DecimalField(default=4.5, max_digits=10, decimal_places=2)),
                ('percentage_from_forex', models.DecimalField(default=4.5, max_digits=10, decimal_places=2)),
                ('added', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('site', models.OneToOneField(default=1, to='sites.Site')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('view_rate', 'View Rates'), ('edit_rate', 'Edit Rates')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rate', models.DecimalField(default=remit.models.current_rate, max_digits=10, decimal_places=2)),
                ('currency_sent', models.CharField(default=b'UGX', max_length=3)),
                ('currency_received', models.CharField(default=b'USD', max_length=3)),
                ('amount_sent', models.DecimalField(max_digits=10, decimal_places=2)),
                ('amount_received', models.DecimalField(max_digits=10, decimal_places=2)),
                ('receiver_number', models.CharField(max_length=130)),
                ('receiver_country_code', models.CharField(default=b'256', max_length=3)),
                ('receiver_fname', models.CharField(default=False, max_length=30, blank=True)),
                ('receiver_lname', models.CharField(default=False, max_length=30, blank=True)),
                ('started_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('added', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('our_charge', models.DecimalField(default=0.0, max_digits=100, decimal_places=2)),
                ('our_percentage', models.DecimalField(default=remit.models.current_percentage, max_digits=10, decimal_places=2)),
                ('total_charge', models.DecimalField(default=0.0, max_digits=10, decimal_places=2)),
                ('visa_response_time', models.DateTimeField(null=True, blank=True)),
                ('visa_response_code', models.CharField(default=False, max_length=30, blank=True)),
                ('visa_response_metadata', models.TextField(default=False, blank=True)),
                ('visa_success', models.BooleanField(default=False)),
                ('visa_processed', models.BooleanField(default=False)),
                ('mobile_response_time', models.DateTimeField(null=True, blank=True)),
                ('mobile_response_code', models.CharField(default=False, max_length=30, blank=True)),
                ('mobile_response_metadata', models.TextField(default=False, blank=True)),
                ('mobile_reason', models.CharField(default=False, max_length=220, blank=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('marked_as_processed', models.BooleanField(default=False)),
                ('processed_on', models.DateTimeField(null=True, blank=True)),
                ('country', models.CharField(default=False, max_length=100, blank=True, choices=[(b'UG', b'Uganda'), (b'KE', b'Kenya'), (b'TZ', b'Tanzania'), (b'RW', b'Rwanda')])),
                ('mobile_network_code', models.CharField(default=False, max_length=100, blank=True, choices=[(b'MTN', b'MTN Mobile Money'), (b'AIRTEL', b'Airtel Money'), (b'UTL', b'M-Sente')])),
                ('sender_country', models.CharField(max_length=30, blank=True)),
                ('processed_by', models.ForeignKey(related_name=b'admin_processed', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('updated_by', models.ForeignKey(related_name=b'admin_update_by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(related_name=b'owner', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('view_transaction', 'View Transactions'), ('edit_transaction', 'Edit Transactions'), ('view_reports', 'View Reports')),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='phonebook',
            unique_together=set([('ext', 'number', 'firstname', 'lastname', 'country_code', 'user')]),
        ),
    ]
