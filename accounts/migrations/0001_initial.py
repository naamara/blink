# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('admin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('country', models.CharField(default=False, max_length=100, blank=True, choices=[(b'UG', b'Uganda'), (b'KE', b'Kenya'), (b'TZ', b'Tanzania'), (b'RW', b'Rwanda')])),
                ('mobile_network', models.CharField(default=False, max_length=100, blank=True, choices=[(b'MTN', b'MTN Mobile Money'), (b'AIRTEL', b'Airtel Money'), (b'UTL', b'M-Sente')])),
                ('is_customer_care', models.BooleanField(default=False)),
                ('user', models.OneToOneField(related_name=b'admin_profile', verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('view_audit_trail', 'View Audit Trails'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LoginInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('login_time', models.DateTimeField(auto_now_add=True)),
                ('user_agent', models.CharField(max_length=1000, null=True, blank=True)),
                ('remote_addr', models.IPAddressField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email_activation_key', models.CharField(max_length=40, verbose_name='activation key', blank=True)),
                ('phone_activation_key', models.CharField(max_length=4, verbose_name='phone activation', blank=True)),
                ('firstname', models.CharField(max_length=50, blank=True)),
                ('lastname', models.CharField(max_length=50, blank=True)),
                ('email_activated', models.BooleanField(default=False)),
                ('userdetails_provided', models.BooleanField(default=False)),
                ('id_verified', models.BooleanField(default=False)),
                ('account_blocked', models.BooleanField(default=False)),
                ('account_verified', models.BooleanField(default=False)),
                ('phone_verified', models.BooleanField(default=False)),
                ('country_code', models.CharField(default=False, max_length=10, blank=True)),
                ('phonenumber', models.CharField(default=False, max_length=20, blank=True)),
                ('address1', models.TextField(default=False, blank=True)),
                ('address2', models.TextField(default=False, blank=True)),
                ('dob', models.DateTimeField(null=True, blank=True)),
                ('country', models.CharField(max_length=50, blank=True)),
                ('city', models.CharField(max_length=30, blank=True)),
                ('id_number', models.CharField(max_length=30, blank=True)),
                ('joined', models.DateTimeField(default=datetime.datetime.now)),
                ('status_updated_on', models.DateTimeField(null=True, blank=True)),
                ('blocked_by', models.ForeignKey(related_name=b'admin_blocked', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('unblocked_by', models.ForeignKey(related_name=b'admin_unblocked', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('unverified_by', models.ForeignKey(related_name=b'admin_unverified', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.OneToOneField(related_name=b'profile', verbose_name='user', to=settings.AUTH_USER_MODEL)),
                ('verified_by', models.ForeignKey(related_name=b'admin_verified', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'permissions': (('view_profile', 'View Profiles'), ('edit_profile', 'Edit Profiles')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserActions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('log_entry', models.ForeignKey(to='admin.LogEntry')),
                ('session', models.ForeignKey(to='accounts.LoginInfo')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
