'''management command to update currencies'''
from django.core.management.base import NoArgsCommand
from time import time
import btc.cryptocharts as cryptocharts
import datetime

RUN_TIME_SECONDS = 60


class Command(NoArgsCommand):

    '''management command'''
    help = """Update our currencies. Fetch\
     the currencies using cryptocharts API\
"""

    def handle_noargs(self, **options):
        start_time = time()
        #last_check_time = None
        print "starting Bitcoin currency update", time() - start_time
        # print "starting standard", time() - start_time
        cryptocharts.runTradingPairUpdate()
        print "finished Bitcoin currency update", datetime.datetime.now()
