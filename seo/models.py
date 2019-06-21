'''Metadata'''
from django.db import models
#from seo.fields import MetaTagField
from django.contrib.auth.models import User
from django.contrib.sites.models import Site


# Create your models here.
class Metadata(models.Model):

    '''remit seo Metadata'''

    class Meta:
        permissions = (
            ('view_seo', 'View SEO'),
            ('edit_seo', 'Edit SEO'),
        )


    site = models.OneToOneField(Site, default=1, unique=True)
    title = models.TextField(blank=False, null=False)
    description = models.TextField(blank=False, null=False)
    keywords = models.TextField(blank=False, null=False)
    extras = models.TextField(blank=True, null=True, default='')
    added_on = models.DateTimeField(null=True, blank=True)
    added_by = models.ForeignKey(User, null=True, blank=True)


    def save(self, *args, **kwargs):
        add = not self.pk
        super(Metadata, self).save(*args, **kwargs)
        if add:
            self.keywords = self.add_keywords(self.keywords)
            self.title = self.add_title(self.title)
            self.description = self.add_description(self.description)
            self.extras = self.add_extras(self.extras)
            super(Metadata, self).save(*args, **kwargs)

    def add_keywords(self, keywords):
        return self.clean_tags(keywords)

    def add_title(self,title):
        return title

    def add_extras(self,title):
        return title

    def add_description(self, description):
        return self.clean_tags(description)

    def clean_tags(self,value):
        return value

    def get_keywords(self):
        return self.format_meta_tag('keywords',self.keywords)

    def get_title(self):
        return self.title

    def get_extras(self):
        return self.extras

    def get_description(self):
        return self.format_meta_tag('description', self.description)

    def format_meta_tag(self, name, value):
        return u'<meta name="%s" content="%s" />' % (name, value)


    #user = models.ForeignKey(User, related_name="owner")
    # rate defaults to current site rate
    #rate = models.DecimalField(
    #    default=current_rate, decimal_places=2, max_digits=10)
    #currency_sent = models.CharField(default='UGX', max_length=3)
    #currency_received = models.CharField(default='USD', max_length=3)
    #amount_sent = models.DecimalField(
    #    null=False, blank=False, decimal_places=2, max_digits=10)
