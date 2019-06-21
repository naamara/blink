'''
Pesapot Django API
'''
from django.conf import settings
import remit.settings as remit_settings
import requests
import json
from remit.utils import debug


class PesaPot():
    """method to make calls to Pesapot api """

    def __init__(self):
        try:
            self.KEY = settings.PESAPOT_KEY
            self.TOKEN = settings.PESAPOT_TOKEN
            self.END_POINT = settings.PESAPOT_URL
        except AttributeError:
            raise AttributeError(
                "Please add PESAPOT_URL, PESAPOT_TOKEN & PESAPOT_KEY to your settings")

    def conn(self, url, data={}, headers={}, method='POST'):
        '''
        connection to api
        '''

        debug('Entered conn', 'testing pesapot', 'paybill')

        headers['Authorization'] = 'Token %s' % self.TOKEN
        headers['AuthorizationKey'] = '%s' % self.KEY
        url = "%s%s" % (
            self.END_POINT,
            url
        )
        debug(url, 'pesapot url', 'paybill')
        req = requests.Request(
            method,
            url,
            headers=headers,
            data=data
        )
        prepared = req.prepare()
        self.pretty_print_POST(prepared)
        s = requests.Session()
        response = {}
        r = s.send(prepared, verify=False)

        temp_r = str(r.__dict__)
        debug(temp_r, 'pesapot con response', 'paybill')
        if r.status_code == 404:
            response = {'errors': {'404', 'Invalid url %s' % url}}
        elif r.status_code == 500:
            response = {'errors': {
                '500', 'An Expception occurred %s, %s' % (url, r.text)}}
        elif r.status_code == 200:
            response = r.text
        try:
            response = json.loads(r.text)
        except Exception, e:
            print e
            pass
        return response

    def QueryMomoAccount(self, msisdn):
        data = {}
        url = 'v1/momo/queryaccount'
        data['msisdn'] = msisdn
        response = self.conn(url, data)

    def DepositMoney(self, msisdn, amount):
        url = 'v1/momo/depositmoney/'
        data = {
            'msisdn': msisdn,
            'amount': amount
        }
        response = self.conn(url, data)
        return response


    def PayBill(self, referencenumber, amount, phonenumber, billtype,names,account_type,area=None,useremit_id=None):
        url = 'v1/paybill/'
        print '::Pesapot useremit_id: ',str(useremit_id)
        data = {
            'referencenum': referencenumber,
            'amount': amount,
            'billtype': billtype,
            'message': 'Hello',
            'phonenumber': phonenumber,
            'paymethod': account_type,
            'names': names,
            'area': area,
            'useremit_id': useremit_id,
        }

        response = self.conn(url, data)
        print '::Response ',str(response)

        return response

    def QueryPayBillAccount(self, referencenumber, billtype, location=""):
        url = 'v1/paybill/queryaccount/'
        data = {
            'referencenum': referencenumber,
            'billtype': billtype,
            'location': location,
        }
        response = self.conn(url, data)
        return response

    def QueryPayBillStatus(self, vendorid):
        url = 'v1/paybill/transactionstatus/'
        data = {
            'vendorid': vendorid,
        }
        response = self.conn(url, data)
        return response


    def TradelanceDeposit(self,receiver_number,amount):
        url = 'v1/tlance/deposit/'
        data = {
            'receiver_number': receiver_number,
            'amount':amount,
        }

        response = self.conn(url,data)

        return response


    def TradelanceRequest(self,receiver_number,amount):
        url = 'v1/tlance/requestpayment/'
        data = {
            'receiver_number': receiver_number,
            'amount':amount,
        }

        response = self.conn(url,data)

        return response

    def TradelanceBalance(self):
        url = 'v1/tlance/balancecheck/'
        data = {
        }

        response = self.conn(url,data)

        return response

    def TradelanceStatus(self, transaction_id):
        url = 'v1/tlance/transactionstatus/'
        data = {
            'transaction_id':transaction_id,
        }

        response = self.conn(url, data)

        return response

    def send_sms(self, to, sms_message):
        url = 'v1/sendsms/residentclient/'
        data = {
            'to': to,
            'sms_message': sms_message,
            'sms_agent': '4',
            'sms_client': 'useremit'
        }

        response = self.conn(url, data)
        return response

    def pretty_print_POST(self, req):
        """
        At this point it is completely built and ready
        to be fired; it is "prepared".

        However pay attention at the formatting used in
        this function because it is programmed to be pretty
        printed and may differ from the actual request.
        """
        print('{}\n{}\n{}\n\n{}'.format(
            '-----------START-----------',
            req.method + ' ' + req.url,
            '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
            req.body,
        ))
