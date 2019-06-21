'''models for btc'''
from django.db import models
from datetime import datetime
from django.contrib.sites.models import Site


class Btc(models.Model):

    ''' btc rates and prices '''
    site = models.OneToOneField(Site, default=1)
    usd = models.DecimalField(
        default=688.00, decimal_places=2, max_digits=10)
    gbp = models.DecimalField(
        default=1114.76, decimal_places=2, max_digits=10)
    buy_usd = models.DecimalField(
        default=1114.76, decimal_places=2, max_digits=10)
    sell_usd = models.DecimalField(
        default=1114.76, decimal_places=2, max_digits=10)
    lastest_usd = models.DecimalField(
        default=1114.76, decimal_places=2, max_digits=10)
    raw = models.TextField(blank=True, null=True)
    modified = models.DateTimeField(default=datetime.now, 
        blank=True)