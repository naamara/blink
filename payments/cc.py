''' Handle cc payments '''
from BeautifulSoup import BeautifulStoneSoup
import urllib
from payments.payment import our_charge
from django.conf import settings
import requests
#import urlparse
from remit.utils import debug
from datetime import datetime
from django.core.urlresolvers import reverse
from remit.forms import sendMoneyForm
from payments.payment import process_mobilemoney, card_charged_email
from remit.models import Transaction
from ipware.ip import get_ip, get_real_ip
from remit import utils


RESPONSE_CODES = {
    'SUCCESS': 'aei7p7yrx4ae34',
}


def check_ipn(request):
    '''check ipn response'''
    response = False
    params = request.GET
    uid = params.get('id', 0)
    ivm = params.get('ivm', 0)
    qwh = params.get('qwh', 0)
    afd = params.get('afd', 0)
    poi = params.get('poi', 0)
    uyt = params.get('uyt', 0)
    ifd = params.get('ifd', 0)
    '''
    url = "https://ipay.intrepid.co.ke/ipn/?vendor=%s&id=%s&ivm=%s&qwh=%s&afd=%s&poi=%s&uyt=%s&ifd=%s" % (settings.IPAY_USER, uid, ivm, qwh, afd, poi, uyt, ifd
                                                                                                  )
    url = "https://ipn.ipayafrica.com/?vendor=%s&id=%s&ivm=%s&qwh=%s&afd=%s&poi=%s&uyt=%s&ifd=%s" % (settings.IPAY_USER, uid, ivm, qwh, afd, poi, uyt, ifd
                                                                                                     )
    '''

    url = "https://ipayafrica.com/ipn/?vendor=%s&id=%s&ivm=%s&qwh=%s&afd=%s&poi=%s&uyt=%s&ifd=%s" % (settings.IPAY_USER, uid, ivm, qwh, afd, poi, uyt, ifd
                                                                                                     )
    debug(url, 'Ipn Check Url', 'ipay')
    try:
        r = requests.get(url, verify=False)
        response = r.text
    except Exception, e:
        debug(e, 'IPN Check Error', 'ipay')
    return response


def process_visa_philip(transaction, result):
    '''start the cc process , check everything here'''
    response = {'error': True, 'status_code': False}
    try:
        transaction.visa_response_metadata = result
        transaction.save()
    except Exception, e:
        debug(e, 'saving transaction metadata', 'process_visa_philip')

    if 'status' in result:
        response['status_code'] = result['status']

    response['metadata'] = result
    transaction.visa_response_time = datetime.now()
    transaction.visa_processed = True

    try:
        visa_result = result['status']
        transaction.visa_response_code = visa_result
        if len(visa_result) > 30:
            visa_result = visa_result[:29]
            transaction.visa_response_code = visa_result
            if 'original_status' in result:
                response['status_code'] = result['original_status']
    except Exception, e:
        debug(e, 'Transaction save error')

    if response['status_code'] == RESPONSE_CODES['SUCCESS']:
        response['error'] = False
        transaction.visa_success = True

    try:
        transaction.save()
    except Exception, e:
        debug(e, 'Transaction save error')
    return response


def prepare_cc_url(request, transaction):
    '''
    handles the processing the cc
    @request  request object
    '''
    user = transaction.user
    callback_url = request.build_absolute_uri(
        reverse('do_cc', args=[transaction.get_invoice()]))
    country_code = user.profile.send_country_code
    amount_sent = our_charge(transaction.amount_sent, country_code)
    url = 'https://www.ipayafrica.com/payments/'
    tel = user.profile.get_ipay_phonenumber()
    params = {'live': settings.LIVE, 'mer': settings.IPAY_MERCHANT, 'oid': transaction.get_order_id(), 'inv': transaction.get_invoice(),
              'ttl': amount_sent, 'tel': tel, 'eml': user.email, 'vid': settings.IPAY_USER, 'cur': 'USD',
              'cbk': callback_url, 'cst': 0, 'hsh': settings.IPAY_HASH_KEY,
              'mm': 0, 'mb': 0, 'dc': 1, 'cc': 1, 'p1': '', 'p2': '', 'p3': '', 'p4': '', 'crl': 0}
    params['hsh'] = ipay_hash(params)
    params = urllib.urlencode(params)
    cc_link = "%s?%s" % (url, params)
    debug(cc_link, 'ipay link', 'ipay')
    return cc_link


def start_cc(transaction, cc_details, request):
    '''start the cc process , check everything here'''
    response = {'error': True, 'status_code': False}
    payload, cc_link = prepare_payload(transaction)
    payload['cvv'] = cc_details['cc_cvc']
    payload['vendor_fname'] = cc_details['cc_fname']
    payload['vendor_lname'] = cc_details['cc_lname']
    payload['ccnum'] = cc_details['cc_number']
    payload['ccmonth'] = cc_details['cc_exp_month']
    payload['ccyear'] = cc_details['cc_exp_year']

    # country code , Area Code and Number
    phonenumber = cc_details['cc_phonnumber']
    payload['cust_PhoneCC'] = phonenumber[:3]
    payload['cust_PhoneAC'] = phonenumber[:3]
    payload['cust_PhoneN'] = phonenumber

    payload['cust_City'] = cc_details['cc_cty']
    payload['cust_Country'] = cc_details['cc_ctry']
    result = submit_form(cc_link, payload, request)

    #
    try:
        #get user ip
        location = None
        user_ip = None
        user_ip = get_real_ip(request, right_most_proxy=True)

        print ':User ip :', str(user_ip)

        if user_ip is not None:
            location = utils.get_user_location(user_ip)
            transaction.location = location
            transaction.save()
        print '::Get User IP Success'
    except Exception as e:
        print '::Get User IP Failed ', str(e)

    try:
        transaction.visa_response_metadata = result
        transaction.save()
    except Exception, e:
        pass

    if 'status_code' in result:
        response['status_code'] = result['status_code']

    if response['status_code'] == RESPONSE_CODES['SUCCESS']:
        response['error'] = False
        transaction.visa_success = True

    response['metadata'] = result
    transaction.visa_response_code = result['status_code']
    transaction.visa_response_time = datetime.now()
    transaction.visa_processed = True
    try:
        transaction.save()
    except Exception, e:
        debug(e, 'Transaction save error')
    return response


def submit_form(cc_link, payload, request):
    '''submit form'''
    try:
        url = 'https://ipay.intrepid.co.ke/inm/ipycc.php'  # % cc_link
        #user_ip =  get_ip(request)
        #debug(user_ip,'Users IP')
        from fake_useragent import UserAgent
        ua = UserAgent()
        headers = {'HTTP_USER_AGENT': ua.random, 'User-Agent': ua.random}
        r = requests.post(url, params=payload, headers=headers)
    except Exception, e:
        debug(e, 'post to ipay error')

    #'REMOTE_ADDR'
    #debug(r.request.headers,'Our Request headers')

    params = {'status_code': False, 'metadata': ''}
    try:
        response_str = str(r.text)
        # debug(response_str)
        params['metadata'] = response_str
        response_str = response_str.split(';')
        if len(response_str) > 0:
            params['transaction_id'] = response_str[0]
        if len(response_str) > 8:
            params['status_code'] = response_str[8]
        if len(response_str) > 15:
            params['msdin'] = response_str[15]
    except Exception, e:
        debug(e, 'error process ipay', 'visa')
    return params


def ipay_hash(p):
    import hmac
    import hashlib
    data = '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (
        p['live'], p['mm'], p['mb'], p['dc'], p['cc'], p['mer'], p[
            'oid'], p['inv'], p['ttl'], p['tel'], p['eml'], p['vid'],
        p['cur'], p['p1'], p['p2'], p['p3'], p['p4'], p['cbk'], p['cst'], p['crl'])
    debug(data, 'ipay hashdata', 'ipay')
    hash_key = hmac.new(settings.IPAY_HASH_KEY, data, hashlib.sha1).hexdigest()
    debug(hash_key, 'ipay hashkey', 'ipay')
    return hash_key


def prepare_payload(transaction):
    '''
    handles the processing the cc
    @request  request object
    '''
    #callback_url = settings.IPAY_CALLBACK_URL
    callback_url = '%s%s' % (settings.BASE_URL, reverse(
        'do_cc', args=[transaction.get_invoice()]))

    user = transaction.user
    amount_sent = our_charge(transaction.amount_sent)
    url = 'https://www.ipayafrica.com/payments/'
    params = {'live': settings.LIVE, 'mer': settings.IPAY_MERCHANT, 'oid': transaction.get_order_id(), 'inv': transaction.get_invoice(),
              'ttl': amount_sent, 'tel': user.profile.get_phonenumber(), 'eml': user.email, 'vid': settings.IPAY_USER, 'cur': 'USD',
              'cbk': callback_url, 'cst': 0, 'hsh': settings.IPAY_HASH_KEY,
              'mm': 0, 'mb': 0, 'dc': 1, 'cc': 1, 'p1': '', 'p2': '', 'p3': '', 'p4': '', 'crl': 1}
    params['hsh'] = ipay_hash(params)
    params = urllib.urlencode(params)
    cc_link = "%s?%s" % (url, params)
    payload = fetch_form(cc_link)
    return (payload, cc_link)


def fetch_form(url):
    '''fetch form data and return '''
    f = urllib.urlopen(url)
    s = f.read()
    f.close()
    soup = BeautifulStoneSoup(s)
    return extract_form_fields(soup)


def extract_form_fields(soup):
    "Turn a BeautifulSoup form in to a dict of fields and default values"
    fields = {}
    for input in soup.findAll('input'):
        # ignore submit/image with no name attribute
        if input['type'] in ('submit', 'image') and not input.has_key('name'):
            continue

        # single element nome/value fields
        if input['type'] in ('text', 'hidden', 'password', 'submit', 'image'):
            value = ''
            if input.has_key('value'):
                value = input['value']
            fields[input['name']] = value
            continue

        # checkboxes and radios
        if input['type'] in ('checkbox', 'radio'):
            value = ''
            if input.has_key('checked'):
                if input.has_key('value'):
                    value = input['value']
                else:
                    value = 'on'
            if fields.has_key(input['name']) and value:
                fields[input['name']] = value

            if not fields.has_key(input['name']):
                fields[input['name']] = value

            continue

        #assert False, 'input type %s not supported' % input['type']

    # textareas
    for textarea in soup.findAll('textarea'):
        fields[textarea['name']] = textarea.string or ''

    # select fields
    for select in soup.findAll('select'):
        value = ''
        options = select.findAll('option')
        is_multiple = select.has_key('multiple')
        selected_options = [
            option for option in options
            if option.has_key('selected')
        ]

        # If no select options, go with the first one
        if not selected_options and options:
            selected_options = [options[0]]

        if not is_multiple:
            assert(len(selected_options) < 2)
            if len(selected_options) == 1:
                value = selected_options[0]['value']
        else:
            value = [option['value'] for option in selected_options]

        fields[select['name']] = value

    return fields


def api_cc(data, request):
    # create the transaction

    response = {
        'status': 'ftr',
        'status_msg': 'The Transaction Failed',
        'invid': 0,
    }
    #debug(data,'Droid Data')
    transaction = False
    mobile_reason = data.get('recipient_message', False)
    transaction_id = data.get('invid', False)
    if transaction_id:
        id = int(transaction_id) ^ 0xABCDEFAB
        try:
            transaction = Transaction.objects.get(
                id=id, user=request.user, is_processed=False, visa_success=False)
        except Exception, e:
            debug(e, 'Fraud', 'fraud')
    else:
        t_data = {'amount_sent': data['amount'], 'receiver_number': data['recipient_number'], 'receiver_fname': data['recipient_firstname'], 'receiver_lname': data['recipient_lastname'],
                  'user': data['user'], 'mobile_reason': mobile_reason,
                  }
        form = sendMoneyForm(t_data)
        if form.is_valid():
            transaction = form.save()
        else:
            response['status_msg'] = form.errors
    if transaction:
        post_values = {'cc_phonnumber': data['cc_phonenumber'], 'cc_ctry': data['cc_country'], 'cc_cty': data['cc_city'], 'cc_lname': data['cc_lastname'], 'cc_fname': data['cc_firstname'], 'cc_exp_year': data['cc_expiry_year'], 'cc_exp_month': data['cc_expiry_month'],
                       'cc_number': data['cc_number'], 'cc_cvc': data['cc_cvv']
                       }

        ipay_response = start_cc(transaction, post_values, request)
        visa_response_code = ipay_response.get('status_code', False)
        if visa_response_code == RESPONSE_CODES['SUCCESS']:
            # send the card charged email
            try:
                card_charged_email(request, transaction)
            except Exception, e:
                debug(e, 'sending card charged email', 'admin')

        yo_response = process_mobilemoney(transaction, response, request)
        yo_response_code = yo_response.get('status', False)
        debug(yo_response_code, 'yo_response_code', 'yo')
        if not yo_response_code == 'ERROR':
            response['status'] = 'str'
        else:
            response['status'] = 'ptr'
            response['status_msg'] = 'The Transaction is pending'
        # debug(yo_response)
        try:
            if transaction:
                response['invid'] = transaction.get_invoice()
        except Exception, e:
            pass
    return response
