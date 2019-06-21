import urllib2
from django.contrib.sites.models import Site


URL = 'http://finance.yahoo.com/d/quotes.csv?e=.csv&f=sl1d1t1&s={from_curr}{to_curr}=X'


def _get_data(url):
    request = urllib2.Request(url, None, {'Accept-encoding': '*'})
    try:
        response = urllib2.urlopen(request)
    except urllib2.URLError:
        return None
    result = response.read()
    return result


def convert(from_curr, to_curr='USD', amount=1.0, percentage_from_forex=4.50):
    '''convert the currency'''
    if from_curr.lower() == to_curr.lower():
        return amount
    data = _get_data(URL.format(from_curr=from_curr, to_curr=to_curr))
    if data:
        exchange = data.split(',')
        try:
            if len(exchange[1]) > 1:
                default = u'{0:.3f}'.format(
                    round(float(exchange[1]) * amount, 3))
            else:
                rate = Site.objects.get_current().rate
                default = rate.get_default_rate(from_curr, to_curr)
        except (IndexError, ValueError):
            rate = Site.objects.get_current().rate
            default = rate.get_default_rate(from_curr, to_curr)

        default = default - percentage(percentage_from_forex, default)
    return default


def percentage(percent, whole):
    '''get the percentage of'''
    return (percent * whole) / 100.0
