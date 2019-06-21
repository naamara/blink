''' Create your models here '''
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.admin.models import LogEntry
from django.utils.deconstruct import deconstructible
import urllib
import hashlib
from remit.utils import COUNTRY_CHOICES, NETWORK_CHOICES
import os
from uuid import uuid4


@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)

path_and_rename = PathAndRename("images/uploads/")

profile_path_and_rename = PathAndRename("images/images/thumbs/")


class AdminProfile(models.Model):

    class Meta:
        permissions = (
            ('view_audit_trail', 'View Audit Trails'),
        )

    '''profile for the admin user'''
    user = models.OneToOneField(User,
                                unique=True,
                                verbose_name=_('user'),
                                related_name='admin_profile')
    country = models.CharField(
        blank=True, max_length=100, choices=COUNTRY_CHOICES, default=False)

    mobile_network = models.CharField(
        blank=True, max_length=100, choices=NETWORK_CHOICES, default=False)

    is_customer_care = models.BooleanField(default=False)

    is_lawyer = models.BooleanField(default=False)
    is_doctor  = models.BooleanField(default=False)
    is_jounalist = models.BooleanField(default=False)
    is_educ = models.BooleanField(default=False)
    category = models.CharField(blank=True, max_length=50, default='')
    cat_name = models.CharField(blank=True, max_length=50, default='')
    doct_name = models.CharField(blank=True, max_length=50, default='')
    phone = models.CharField(blank=True, max_length=50, default='')
    region = models.CharField(blank=True, max_length=50, default='')
    districts = models.CharField(blank=True, max_length=50, default='')
    info = models.CharField(blank=True, max_length=800, default='')
    date_joined = models.DateTimeField(default=datetime.now)



    def __str__(self):
        return str(self.is_lawyer)



    @property
    def uid(self):
        '''return user'''
        return str(self.pk ^ 0xABCDEFAB)

    @property
    def permissions(self):
        '''get a stuff users permissions'''
        user_permissions = {}
        for x in Permission.objects.filter(user=self.user):
            user_permissions.update({x.codename: True})
        return user_permissions

    @property
    def avatar(self, size="100"):
        '''gravatar image'''
        gravatar_url = settings.GRAVATAR_URL
        gravatar_url += urllib.urlencode({
            'gravatar_id': hashlib.md5(self.user.email).hexdigest(),
            'size': str(size)
        })
        return gravatar_url


class Profile(models.Model):

    '''user profile information'''

    class Meta:
        permissions = (
            ('view_profile', 'View Profiles'),
            ('edit_profile', 'Edit Profiles'),
        )

    '''Profile for normal user'''
    user = models.OneToOneField(User,
                                unique=True,
                                verbose_name=_('user'),
                                related_name='profile')
    email_activation_key = models.CharField(_('activation key'),
                                            max_length=40,
                                            blank=True)
    phone_activation_key = models.CharField(_('phone activation'),
                                            max_length=4,
                                            blank=True)
    firstname = models.CharField(blank=True, max_length=50)
    lastname = models.CharField(blank=True, max_length=50)
    email_activated = models.BooleanField(default=False)
    userdetails_provided = models.BooleanField(default=False)
    id_verified = models.BooleanField(default=False)
    id_scanned = models.BooleanField(default=False)
    id_scan_ref = models.CharField(blank=True, max_length=50)
    id_verify_ref = models.CharField(blank=True, max_length=50)
    account_blocked = models.BooleanField(default=False)
    account_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    country_code = models.CharField(blank=True, default=False, max_length=10)
    phonenumber = models.CharField(blank=True, default=False, max_length=20)
    address1 = models.TextField(blank=True, default=False)
    address2 = models.TextField(blank=True, default=False)
    dob = models.DateTimeField(null=True, blank=True)
    country = models.CharField(blank=True, max_length=50)
    city = models.CharField(blank=True, max_length=30)
    id_number = models.CharField(blank=True, max_length=30)
    signup_location = models.CharField(blank=True, default=False, max_length=600)

    #id_pic = models.ImageField(upload_to=path_and_rename("images/uploads/"), blank=True)
    id_pic = models.ImageField(upload_to="images/uploads/", blank=True)

    id_type = models.CharField(blank=True, max_length=30)
    id_expiry = models.CharField(blank=True, max_length=30)
    joined = models.DateTimeField(default=datetime.now)
    blocked_by = models.ForeignKey(
        User, null=True, blank=True, related_name="admin_blocked")
    verified_by = models.ForeignKey(
        User, null=True, blank=True, related_name="admin_verified")
    verification_attempts = models.IntegerField(default=0)
    unverified_by = models.ForeignKey(
        User, null=True, blank=True, related_name="admin_unverified")
    unblocked_by = models.ForeignKey(
        User, null=True, blank=True, related_name="admin_unblocked")
    status_updated_on = models.DateTimeField(null=True, blank=True)

    # profile_pic = models.ImageField(
    #    upload_to=path_and_rename("images/images/thumbs/"), blank=True)
    profile_pic = models.ImageField(upload_to="images/images/thumbs/",
                                    blank=True
                                    )
    #is_bitcoin_user = models.BooleanField(default=False)

    # profile_pic = models.ImageField(
    #    upload_to=profile_path_and_rename, null=True, blank=True)
    send_country_code = models.CharField(
        blank=False, default='256', max_length=10)

    # get the current rate for the user
    def current_rate(self):
        '''get the curent rate of the User'''
        from remit.models import Country
        return Country.objects.get(dailing_code=self.send_country_code).rates
        

    def current_rate(self):
        from remit.models import Country
        return Country.objects.get(dailing_code=self.send_country_code).rates

        
    def passport_extension(self):
        name, extension = os.path.splitext(self.id_pic.name)
        return extension

    def get_phonenumber(self):
        '''
        Return a users phonenumber
        '''
        return str('%s%s' % (self.country_code, self.phonenumber))


    def get_ipay_phonenumber(self):
        '''
        Return a users phonenumber for ipay form
        '''
        tel = self.get_phonenumber()
        try:
            if len(tel) < 1:
                tel = settings.CONTACT_NO
            tel = tel.replace('+', '')
        except Exception, e:
            pass
        return tel

    def get_names(self):
        '''
        Return a users phonenumber
        '''
        text = '%s %s' % (self.firstname, self.lastname)
        try:
            text = text.encode('utf-8')
        except UnicodeEncodeError:
            pass
        return text

    def user_can_sendmoney(self):
        '''
        If a user is a allowed to send money
        '''
        can_send = self.userdetails_provided
        return can_send

    @models.permalink
    def admin_url(self):
        '''return admin url link'''
        # print self.uid
        return ('admin:admin_user', ({"pk": self.uid}), {})
        #url = reverse('admin:admin_user', kwargs={self.uid})
        # return str(url)
        # return str(settings.BASE_URL + 'admin/user/%s' % (self.uid()))

    @models.permalink
    def get_unique_url(self):
        '''
        direct link to profile
        '''
        return('profile', [str(self.pk ^ 0xABCDEFAB)])

    def __unicode__(self):
        return str('%s %s' % (self.firstname, self.lastname))

    @property
    def uid(self):
        return str(self.pk ^ 0xABCDEFAB)

    @property
    def avatar(self, size="100"):
        '''gravatar image'''
        profile_pic = self.profile_pic
        if not profile_pic:
            gravatar_url = settings.GRAVATAR_URL
            gravatar_url += urllib.urlencode({
                'gravatar_id': hashlib.md5(self.user.email).hexdigest(),
                'size': str(size)
            })
        else:
            gravatar_url = profile_pic.url
        return gravatar_url


class LoginInfo(models.Model):
    '''store login data'''
    login_time = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(max_length=1000, blank=True, null=True)
    remote_addr = models.IPAddressField()
    user = models.ForeignKey(User, blank=False, null=False)


class UserActions(models.Model):
    '''store user actions'''
    session = models.ForeignKey(LoginInfo, blank=False, null=False)
    log_entry = models.ForeignKey(LogEntry, blank=False, null=False)
    user = models.ForeignKey(User, blank=False, null=False)

    @property
    def user_location(self):
        location = 'UnKnown'
        try:
            if self.session.remote_addr:
                import requests
                r = requests.get('http://ipinfo.io/%s/json' %
                                 self.session.remote_addr)
                loc = r.json()
                if 'ip' in loc:
                    location = '%s' % loc['ip']
                if 'country' in loc:
                    location += ',%s' % loc['country']
                if 'city' in loc:
                    location += ',%s' % loc['city']
                if 'region' in loc:
                    location += ',%s' % loc['region']
        except Exception, e:
            pass
        return location





class Create_staff_User(models.Model):

    '''user profile information'''

    '''Profile for normal user'''
    user = models.OneToOneField(User,default="")
    username = models.CharField(blank=True, max_length=50)
    email = models.CharField(blank=True, max_length=50)
    category = models.CharField(blank=True, max_length=50)
    cat_name = models.CharField(blank=True, max_length=50)
    doct_name = models.CharField(blank=True, max_length=50)
    role = models.CharField(blank=True, max_length=100)
    password = models.CharField(blank=True, max_length=100)
    phone = models.CharField(blank=True, max_length=50)
    region = models.CharField(blank=True, max_length=50)
    districts = models.CharField(blank=True, max_length=50)
    info = models.TextField()
    date_joined = models.DateTimeField(default=datetime.now)



class AddInfo(models.Model):

    '''user profile information'''

    '''Profile for normal user'''
    info = models.TextField()
    