from CryptoCoinChartsApi import API
from btc.models import Btc
from btc.forms import AddBtcForm
from decimal import Decimal
import urllib2
import simplejson
from django.contrib.sites.models import Site


def runTradingPairUpdate():
    '''run tradingpair updates'''
    try:
        btc = Site.objects.get_current().btc
    except Exception, e:
        debug(e)
        # create the rates if we don't have them
        btc = Btc(site=Site.objects.get_current())
        btc.save()
    data = fetchAPITradingPairData()
    form = AddBtcForm(data,instance=btc)
    if form.is_valid():
        form.save()
    else:
        debug(form.errors,'Save BTC errors')





def fetchAPITradingPairData():
    '''fetch trading data from BlockChain'''
    print "Fetching Data from Blockchain.info____"
    url = 'https://blockchain.info/ticker'
    try:
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        f = opener.open(url)
        tradingpair = simplejson.load(f)
    except Exception, e:
        debug(e)
    pb = {}
    if tradingpair:
        debug(tradingpair, 'tradingpair')
        usd = tradingpair['USD']
        gbp = tradingpair['GBP']
        try:
            pb['usd'] = Decimal(
                usd['15m']).quantize(Decimal("0.00"))
            pb['gbp'] = Decimal(
                gbp['15m']).quantize(Decimal("0.00"))
            pb['buy_usd'] = Decimal(
                usd['buy']).quantize(Decimal("0.00"))
            pb['sell_usd'] = Decimal(
                usd['sell']).quantize(Decimal("0.00"))
            pb['raw'] = tradingpair
        except Exception, e:
            debug(e)
    return pb


def btc_to_ugx(price=1):
    '''convert btc to ugx'''
    btc = Site.objects.get_current().btc
    rates = Site.objects.get_current().rate
    btc_to_usd = Decimal(btc.usd) * Decimal(price)
    usd_to_ugx = Decimal(rates.usd_to_ugx)
    #debug(btc_to_usd,'USD to ugx')
    btc_to_ugx_rate = btc_to_usd * usd_to_ugx
    debug(btc_to_ugx_rate ,'BTC TO UGX')
    return btc_to_ugx_rate  

def btc_to_usd(price=1):
    '''convert btc to ugx'''
    btc = Site.objects.get_current().btc
    rates = Site.objects.get_current().rate
    return Decimal(btc.usd) * Decimal(price)


def debug(data, txt=False):
    from remit.utils import debug as ndebug
    return ndebug(data, txt)
