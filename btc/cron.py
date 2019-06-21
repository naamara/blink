'''Get and Update Coinlists and Trading Pairs'''
import os
#from django.core.management import setup_environ
#import cryptocoins.settings as settings
# setup_environ(settings)
#import cryptocoins.cryptocharts as cryptocharts
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "btc.settings")
# django.setup()
import btc.cryptocharts as cryptocharts
cryptocharts.runTradingPairUpdate()
