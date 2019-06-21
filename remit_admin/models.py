'''django admins for support'''
from django.db import models
#from django.contrib.sites.models import Site
# Create your models here.
from django.contrib.auth.models import User
from datetime import datetime

#from remit.utils import  debug

class EmailSupport(models.Model):
    '''email support'''

    EMAIL_REASON = (
    ('ACCOUNT_VERIFICATION', 'ACCOUNT VERIFICATION'),
    ('PENDING_TRANSACTION', 'PENDING TRANSACTION'),
    ('FAILED_TRANSACTION', 'FAILED TRANSACTION'),
    ('OTHER', 'OTHER'),
    )

    user = models.ForeignKey(User, related_name="email_owner")
    support_staff = models.ForeignKey(User, related_name="support_user")
    msg = models.TextField(blank=False)
    subject = models.CharField(max_length = 100)
    added = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(
        blank=True, max_length=100, choices=EMAIL_REASON, default=False)

    @property
    def user_profile(self):
        from accounts.models import Profile
        '''
        owner profile
        '''
        return Profile.objects.get(user=self.user.pk)

    @property
    def support_staff_profile(self):
        from accounts.models import Profile
        '''
        owner profile
        '''
        return Profile.objects.get(user=self.support_staff.pk)


class add_health_info(models.Model):

    user = models.OneToOneField(User,default="")
    title_health = models.CharField(blank=True, max_length=255)
    message = models.TextField(blank=True, max_length=900)
    when = models.DateTimeField(default=datetime.now)



class HealthInfo(models.Model):

    sub = models.CharField(blank=True, max_length=255)
    msg = models.TextField(blank=True, max_length=900)
    when = models.DateTimeField(default=datetime.now)


class LawhInfo(models.Model):

    sub = models.CharField(blank=True, max_length=255)
    msg = models.TextField(blank=True, max_length=900)
    when = models.DateTimeField(default=datetime.now)


class JounalisthInfo(LawhInfo):
    pass


class EducationInfo(LawhInfo):
    pass

