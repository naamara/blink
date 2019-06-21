"""
Methods for processing our visa,mastercard transactions
"""
import requests
from datetime import datetime
from payments.mtn import Mtn
import remit.settings as settings
from remit.utils import mailer, sendsms, admin_mail, debug, get_site_admin, get_mobile_network_code
from django.contrib.sites.models import Site
from decimal import Decimal
from django.utils import timezone
from pesapot.pesapot import PesaPot
from yopay import yopay
import json
from ipware.ip import get_ip, get_real_ip
from remit import utils
from utils import format_sms_message

RESPONSE_CODES = {
    'SUCCESS': 'aei7p7yrx4ae34',
}


def check_source(request):
    source = True
    values_to_check = ['id', 'ivm', 'txncd']
    for x in values_to_check:
        if not x in request.GET:
            source = False
    return source


def mobile_provider_charge(num):
    '''get the charge of the mobile provided'''
    charge = 0
    if settings.OTHER_FEES:
        rates = Site.objects.get_current().rate
        charge = rates.mtn_charge
        airtel = ('70', '75')
        if num in airtel:
            charge = rates.airtel_charge
    return charge


def process_transaction(request):
    data = request.GET
    name = data['id']
    id = False
    try:
        id = int(name) ^ 0xABCDEFAB

    except Exception, e:
        debug(e, 'checking transaction')
        log_fraud(request)
    # transaction = get_object_or_404(Transaction.objects.filter(
    #    id=id, visa_processed=False), id=id, visa_processed=False)
    transaction = get_object_or_404(Transaction.objects.filter(id=id), id=id)

    # try:
    #     #get user ip
    #     location = None
    #     user_ip = None
    #     user_ip = get_real_ip(request, right_most_proxy=True)
    #
    #     print ':User ip :', str(user_ip)
    #
    #     if user_ip is not None:
    #         location = utils.get_user_location(user_ip)
    #         transaction.location = location
    #         transaction.save()
    #     print '::Get User IP Success'
    # except Exception as e:
    #     print '::Get User IP Failed ', str(e)

    response = process_visa(transaction, request)
    # do the mobile money if we have success from the visa
    # if not response['error'] and response['status_code'] == 'aei7p7yrx4ae34':
    if not response['error'] and response['status_code'] == RESPONSE_CODES['SUCCESS']:
        if transaction.utility:
            '''this is a utility bill'''
            response = process_utility(transaction, response, request)
        else:
            response = process_mobilemoney(transaction, response, request)
        try:
            card_charged_email(request, transaction)
        except Exception, e:
            debug(e, 'sending card charged email', 'admin')
    return response


def process_utility(transaction, response, request=False, processed_by=False, mark_as_processed=False):
    pesapot = PesaPot()
    amount = transaction.actual_amount_received
    referencenum = transaction.referencenumber
    billtype = transaction.billtype
    phonenumber = transaction.paybill_recipient_number()
    area = transaction.billarea
    useremit_id = str(transaction.hashid)

    print ':Useremit ID: ', useremit_id

    names = transaction.utility_account_name
    account_type = transaction.utility_account_type
    response = pesapot.PayBill(
        referencenum,
        amount,
        phonenumber,
        billtype,
        names,
        account_type,
        area,
        useremit_id,
    )
    try:
        #receipt_id = response.get('receipt_id','')
        transaction.mobile_response_metadata = response
        response.get('')
        #transaction.utility_receipt_id = receipt_id
        #print '::Pegasus Receipt ID ',str(receipt_id)
        transaction.save()
    except Exception, e:
        debug(e, 'saving transaction response', 'billpayment')
    return response

def process_successful_utility(transaction,request=False, ):
    phone_number = transaction.receiver_number
    sender_number = transaction.sender_number()
    recipient_number = transaction.recipient_number()
    country_code = int(transaction.receiver_country_code)

    try:
        #send sms to sender
        send_transaction_sms_notification(
            sender_number, transaction, 'success_sender')

        #send sms to receiver
        send_transaction_sms_notification(
            recipient_number, transaction, 'success_receiver')

        # send email to sender
        transaction_delivered_email(request, transaction)

        # send email to admins
        admin_mail(request, 'complete_transaction', transaction)

        print ':Sms, Email success'
    except Exception as e:
        print ':Sms Email failure ', str(e)


def process_mobilemoney(transaction, response, request=False, processed_by=False, mark_as_processed=False):
    '''process mobile money'''
    phone_number = transaction.receiver_number
    mtn = Mtn()
    country_code = int(transaction.receiver_country_code)
    data = False

    if mark_as_processed:
        data = {'status': 'Ok', 'statuscode': '0'}

    elif country_code == 256:

        if not settings.DISABLE_MTN and get_mobile_network_code(phone_number) == 'MTN':
            '''process mtn check number'''
            mtn = Mtn()
            try:
                check_kyc = mtn.kyc_check(phone_number)
                if check_kyc:
                    data = mtn.DepositMoney(
                        amount, phone_number, transaction.hashid, ref_text)
                else:
                    data = {
                        'status': 'KYC Not Verified',
                        'KYC': 'KYC Not Verified',
                        'request': request
                    }
            except Exception, e:
                debug(e, 'Mtn pay withdrawal error', 'mtn')

        if settings.ENABLE_TRADELANCE:
            '''
            deliver money to mobile via tradelance
            '''
            print ':Inside tradelance'
            print ':Phonenumber: ',str(phone_number)
            print ':Mobile network code: ',str(get_mobile_network_code(phone_number))
            if get_mobile_network_code(phone_number) == 'AIRTEL' and settings.DISABLE_AIRTEL_MONEY:
                print 'AIRTEL Money disabled'
                debug('Airtel money disabled', 'Tradelance deposit error', 'tradelance')

                data = {
                    'status':'ERROR',
                    'tradelance_error_description':'Airtel Money disabled'
                }
                #return None

            elif get_mobile_network_code(phone_number) == 'MTN' and settings.DISABLE_MTN_MOBILE_MONEY:
                print 'MTN MObile money disabled'
                debug('MTN MObile money disabled', 'Tradelance deposit error', 'tradelance')

                data = {
                    'status':'ERROR',
                    'tradelance_error_description':'MTN MOBILE Money disabled'
                }
                #return None

            else:
                try:
                    print ':Processing tradelance'
                    debug('tradelance', 'Tradelance deposit entered', 'tradelance')
                    pesapot = PesaPot()
                    amount = transaction.actual_amount_received
                    receiver_number = transaction.recipient_number()

                    #true_african(used for tradelance airtel deposit) doesnt support decimals.
                    if get_mobile_network_code(phone_number) == 'AIRTEL':
                        try:
                            received_amount = int(transaction.actual_amount_received)
                            amount = received_amount
                            #transaction.actual_amount_received = amount
                            #transaction.save()
                        except Exception as e:
                            print ':Airtel tlance error ', str(e)

                    response_data = pesapot.TradelanceDeposit(receiver_number,amount)

                    print '::TLACNE RESPONSE: ',str(response_data)

                    if response_data.get('StatusCode') == "200" or response_data.get('Status') == "SUCCESS":
                        data = {}
                        data['response'] = response_data
                        data['status'] = 'Ok'
                        data['statuscode'] = '0'
                    else:
                        data = {
                            'status':'ERROR',
                            'tradelance_error_description':response_data.get('ErrorDescription',''),
                            'transaction_response_id':response_data.get('Reference','')
                        }

                except Exception as e:
                    debug(e, 'Tradelance deposit error', 'tradelance')

        elif settings.ENABLE_YO:
            '''
            process yo payments
            '''
            yo = yopay()
            try:
                number = transaction.recipient_number()
                data = yo.withdraw(amount, number, ref_text)
            except Exception, e:
                debug(e, 'Yo pay withdrawal error', 'yo')


        # mtn = Mtn()
        # amount = transaction.amount_received
        # phone_number = transaction.receiver_number
        # ref_text = transaction.sender_reason()
        # if get_mobile_network_code(phone_number) == 'MTN':
        #     if not settings.DISABLE_MTN:
        #         '''process mtn check number'''
        #         try:
        #             check_kyc = mtn.kyc_check(phone_number)
        #             if check_kyc:
        #                 data = mtn.DepositMoney(
        #                     amount, phone_number, transaction.hashid, ref_text)
        #             else:
        #                 data = {
        #                     'status': 'KYC Not Verified',
        #                     'KYC': 'KYC Not Verified',
        #                     'request': request
        #                 }
        #         except Exception, e:
        #             debug(e, 'Mtn pay withdrawal error', 'mtn')
        #
        # else:
        #
        #     yo = yopay()
        #     try:
        #         number = transaction.recipient_number()
        #         data = yo.withdraw(amount, number, ref_text)
        #     except Exception, e:
        #         debug(e, 'Yo pay withdrawal error', 'yo')

    elif country_code == 254:
        from payments.ipay import ipay
        ipay = ipay()
        try:
            data = ipay.withdraw(transaction)
        except Exception, e:
            debug(e, 'Ipay Bulk withdrawal error', 'ipay')
    elif country_code == 250:
        from payments.rwanda import Rwanda
        rwanda = Rwanda()
        try:
            data = rwanda.withdraw(transaction)
        except Exception, e:
            debug(e, 'Rwanda Bulk withdrawal error', 'rwanda')

    if data:
        if not mark_as_processed:
            try:
                transaction.mobile_response_metadata = data
                transaction.save()
            except Exception, e:
                pass

        transaction_status = data.get('status', '')
        transaction_status_code = data.get('statuscode', '')
        transaction_response_id = data.get('transaction_response_id', '')
        if transaction_status == 'Ok' or transaction_status_code == '0' or transaction_status_code == 0:
            response['delivered_to_mobile'] = True
            response['error'] = False

            try:
                '''transaction_id stored in mobile_response_code'''
                transaction.mobile_response_code = transaction_response_id
                transaction.save()
            except Exception, e:
                print e

            try:
                transaction.is_processed = True
                transaction.save()
            except Exception, e:
                debug(e, 'is_processed save error')
            try:
                transaction.processed_on = timezone.now()
                transaction.save()
            except Exception, e:
                debug(e, 'Save time error')

            '''This whole section really needs to go into signaling process , celery or something'''
            if request:
                # send sms to sender
                # smsdata = {'code':'success_sender','data':transaction}

                sender_number = transaction.sender_number()
                send_transaction_sms_notification(
                    sender_number, transaction, 'success_sender')

                # send sms to receiver
                # smsdata = {'code':'success_receiver','data':transaction}
                recipient_number = transaction.recipient_number()

                try:
                    send_transaction_sms_notification(
                        recipient_number, transaction, 'success_receiver')

                except Exception as e:
                    print 'Failes to send sms: ',str(e)


                # send_transaction_sms_notification(
                #     recipient_number, transaction, 'success_receiver')

                # send email to sender
                transaction_delivered_email(request, transaction)

                # send email to admins
                admin_mail(request, 'complete_transaction', transaction)

            try:
                if processed_by:
                    transaction.processed_by = processed_by
                else:
                    '''Processed by blank Admin'''
                    transaction.processed_by = get_site_admin()
            except Exception, e:
                pass
        else:
            if not processed_by:
                '''send email to admins only once'''
                admin_mail(request, 'pending_transaction', transaction)

            if 'statuscode' in data:
                transaction.mobile_response_code = data['statuscode']
                transaction.marked_as_processed = mark_as_processed
                transaction.mobile_response_time = datetime.now()
                try:
                    transaction.save()
                except Exception, e:
                    debug(e, 'Transaction Save error')
    return response


def process_visa(transaction, request):
    '''
    process the visa part of the transaction
    '''
    response = {'error': True}
    data = request.GET
    # response code defaults to failed
    visa_response_code = 'bdi6p2yy76etrs'
    if 'status' in data:
        visa_response_code = data['status']
    if visa_response_code == RESPONSE_CODES['SUCCESS']:
        response['error'] = False
        transaction.visa_success = True

    response['metadata'] = data
    response['status_code'] = visa_response_code
    transaction.visa_response_code = visa_response_code
    transaction.visa_response_time = datetime.now()
    transaction.visa_response_metadata = response
    transaction.visa_processed = True

    try:
        transaction.save()
    except Exception, e:
        debug(e, 'Transaction save error')
    return response


def transaction_delivered_email(request, transaction):
    template = None

    if transaction.utility:
        template = template = settings.EMAIL_TEMPLATE_DIR + 'billtransaction.html'

    else:
        template = template = settings.EMAIL_TEMPLATE_DIR + 'transaction.html'

    #template = settings.EMAIL_TEMPLATE_DIR + 'transaction.html'
    c = {'mobile_money_sent': True, 'data': transaction}
    mailer(
        request, 'Delivery Notification (useremit.com - Redcore Interactive)',
        template, c, transaction.user.email)


def card_charged_email(request, transaction):
    email = transaction.user.email
    template = None
    if transaction.utility:
        template = settings.EMAIL_TEMPLATE_DIR + 'bill_credit_card_charged.html'
    else:
        template = settings.EMAIL_TEMPLATE_DIR + 'credit_card_charged.html'

    #template = settings.EMAIL_TEMPLATE_DIR + 'credit_card_charged.html'
    c = {'subject':
         'Successful Payment (useremit.com - Redcore Interactive)',
         'data': transaction
         }
    mailer(request, 'Successful Payment (useremit.com - Redcore Interactive)',
           template, c, email)


def send_transaction_sms_notification(phonenumber, data, code):
    '''send transactionsms'''
    template = None
    yaka_token = data.utility_pegpay_id
    receipt_id = data.utility_receipt_id
    num = "%s" % phonenumber

    if data.utility:
        # try:
        #     import ast
        #     model_data = data.mobile_response_metadata
        #     utility_data = ast.literal_eval(model_data)
        #     if data.billtype == '1' and data.utility_account_type == 'PREPAID':
        #
        #         yaka_token = utility_data['yaka_token']
        #
        #     #receipt_id = data.utility_receipt_id
        #     print '::JSON success ', str(receipt_id)
        # except Exception as e:
        #     print '::JSON SMS ERROR ', str(e)

        template = settings.SMS_TEMPLATE_DIR + 'billsms.html'
    else:
        template = settings.SMS_TEMPLATE_DIR + 'transactionsms.html'

    #template = settings.SMS_TEMPLATE_DIR + 'transactionsms.html'
    response = True
    try:
        transaction_data = {
            'amount_sent': str(data.amount_sent),
            'recipient_number': data.recipient_number(),
            'actual_amount_received': str(data.actual_amount_received),
            'display_amount_received': str(data.display_amount_received()),
            'sender_names': data.sender_names(),
            'sender_reason': data.sender_reason(),
            'transactionid': data.hashid,
            'referencenumber': data.referencenumber,
            'billtype': data.billtype,
            'mobile_response_code': data.mobile_response_code,
            'get_invoice':data.get_invoice(),
            'amount_received':str(data.amount_received),
            'receipt_id': receipt_id,
            'yaka_token': yaka_token,
            'our_charge': str(data.our_charge),
            'total_charge':str(data.total_charge),
        }
        #'amount_sent': float(data.amount_sent)
        #actual_amount_received': float(data.actual_amount_received)
        #json_data = json.dumps(transaction_data)



        #use africa sms for non american numbers.
        if settings.USE_AFRICA_SMS and num[0] != '1':
            
            try:
                pesapot = PesaPot()
                country_code = int(data.receiver_country_code)

                message = format_sms_message(template,{'data': transaction_data, 'code': code})
                print ':Africa Sms message ', message
                response = pesapot.send_sms(
                    data.recipient_number(),
                    message
                )
                print ':Send africa sms success'
                debug(response, 'response sms response', 'sms')
            except Exception as e:
                print '::Africa sms error: ',str(e)

        else:
            response = sendsms(phonenumber, template, {'data': transaction_data, 'code': code})
            debug(response, 'response sms response', 'sms')

    except Exception, e:
        debug(e, 'Send transaction sms error')
    return response


def log_fraud(request):
    try:
        debug(request.GET, 'Fraud', 'fraud')
    except Exception, e:
        pass
    return False


def our_charge(amount, country_code):
    '''our charge'''
    from remit.models import Country
    rates = Country.objects.get(dailing_code=country_code).rates
    amount = Decimal(amount)
    our_charge_usd = Decimal(rates.transfer_fee_percentage)
    print our_charge_usd
    our_charge_usd = our_charge_usd * amount
    our_charge_usd = Decimal(our_charge_usd) / Decimal(100)
    amount = our_charge_usd + amount
    amount = round(amount, 2)
    return amount


def ugx_charge(number):
    charge = 0
    network = ''
    # network = get_network(number)
    if network == 'AIRTEL':
        charge = 300
    elif network == 'MTN':
        charge = 377
    return charge
