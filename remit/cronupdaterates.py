from remit.converter import convert
from remit.models import Rate
from decimal import Decimal
from django.contrib.sites.models import Site


def cron_update_rates():
    rate = Site.objects.get_current().rate
    # do percentage_from_forex
    rate.usd_to_ugx = convert(from_curr='USD', to_curr='UGX')
    rate.usd_to_kes = convert(from_curr='USD', to_curr='KES')
    rate.usd_to_tzs = convert(from_curr='USD', to_curr='TZS')
    rate.save()
