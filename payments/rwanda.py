''' ipay '''
import remit.settings as settings
import urllib
from remit.utils import debug
import requests


class Rwanda():

    def __init__(self):
        self.settings = settings

    def withdraw(self, transaction):
        from pesapot.pesapot import PesaPot
        p = PesaPot()
        amount = transaction.actual_amount_received
        try:
            amount = int(round(amount, 0))
        except Exception, e:
            debug(e, 'amount_received', 'ipay')
        msisdn = transaction.recipient_number()
        response = p.DepositMoney(msisdn=msisdn, amount=amount)
        params = {}
        try:
            params['metadata'] = response
            responsecode = response.get('responsecode')
            responsecode = int(responsecode)
            transactionid = response.get('transactionid', None)
            params['statuscode'] = responsecode
            params['status'] = responsecode
            if responsecode == 4:
                params['status'] = 'Ok'
                params['transaction_id'] = transactionid
        except Exception, e:
            debug(e, 'error process Rwanda', 'Rwanda')
        return params
