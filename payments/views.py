'''Payment views'''
from django.shortcuts import render, get_object_or_404, redirect
from django.template.response import TemplateResponse
from remit.forms import doCCForm
from remit.utils import debug, success_message, error_message
from remit.models import Transaction, WalletTransaction
from payments.cc import start_cc, check_ipn
from remit.decorators import login_required
from payments.payment import process_mobilemoney, card_charged_email, process_utility
from remit.misc import COUNTRY_CODES
from django.core.urlresolvers import reverse
from ipware.ip import get_ip, get_real_ip
from remit import utils
from django.shortcuts import HttpResponse, render_to_response, \
    HttpResponseRedirect, render


def render_view(request, template, data):
    ''' render_view '''
    '''
    wrapper for rendering views , loads RequestContext
    @request  request object
    @template  string
    @data  tumple
    '''
    return render(request, template,
        data)

from django.db.models import AutoField
def copy_model_instance(obj):
    """Create a copy of a model instance.

    M2M relationships are currently not handled, i.e. they are not
    copied.

    See also Django #4027.
    """
    initial = dict([(f.name, getattr(obj, f.name))
                    for f in obj._meta.fields
                    if not isinstance(f, AutoField) and\
                       not f in obj._meta.parents.values()])
    return obj.__class__(**initial)


@login_required
def do_cc(request, name):
    '''new cc method'''
    id = int(name) ^ 0xABCDEFAB
    transaction = get_object_or_404(Transaction.objects.filter(id=id, user=request.user,is_processed=False, visa_success=False), id=id, user=request.user, is_processed=False, visa_success=False)
    is_utility = transaction.utility
    from_wallet = transaction.from_wallet
    from payments.cc import prepare_cc_url, process_visa_philip
    from payments.forms import CheckIpayForm
    cc_link = prepare_cc_url(request, transaction)
    transaction_url = request.build_absolute_uri(reverse('do_cc', args=[transaction.get_invoice()]))


    if 'status' in request.GET and 'txncd' in request.GET:
        # do ipn
        ipay_form = CheckIpayForm(request.GET)
        if ipay_form.is_valid():
            result = {'status':ipay_form.cleaned_data['status'], 'txncd':ipay_form.cleaned_data['txncd'],
            'msisdn_id':ipay_form.cleaned_data['msisdn_id']
            }

            try:
                result['original_status'] = ipay_form.cleaned_data['status']
                ipn_check = check_ipn(request)
                result['ipn_check_status'] = ipn_check
            except Exception, e:
                debug(e,'saving ipn status','ipay')


            if ipn_check:
                result['status'] = ipn_check
            response = process_visa_philip(transaction, result)


            if not response['error']:
                #if visa is successful , do mobile transaction
                if is_utility:
                    response = process_utility(transaction, response, request)
                else:
                    response = process_mobilemoney(transaction, response, request)
                try:
                    card_charged_email(request, transaction)
                except Exception, e:
                    debug(e,'sending card charged email','admin')
                if is_utility:
                    debug(response,'paybill response','paybill')
                    home_url = request.build_absolute_uri(reverse('paybill'))
                    if 'errors' in response:
                        error_message(request, 'process_utility',
                        {'transaction':transaction,'delivered_to_mobile': False}
                        )
                    else:
                        success_message(request, 'process_utility',
                            {'transaction':transaction, 'delivered_to_mobile': False}
                            )
                elif from_wallet:
                    home_url = request.build_absolute_uri(reverse('wallet'))
                    if 'errors' in response:
                        error_message(request, 'process_wallet',
                        {'transaction':transaction,'delivered_to_mobile': False}
                        )
                    else:

                        success_message(request, 'process_wallet',
                            {'transaction':transaction, 'delivered_to_mobile': True}
                            )
                        try:
                            wallettransaction = WalletTransaction.objects.get(transaction=transaction)
                            wallettransaction.is_debit = False
                            wallettransaction.modified_by = request.user
                            wallettransaction.save()
                        except Exception, e:
                            debug(e, 'wallet response', 'wallet')
                        try:
                            transaction.is_processed=True
                            transaction.save()
                        except Exception, e:
                            debug(e, 'Built wallet response', 'wallet')
                            pass

                else:
                    delivered_to_mobile = False
                    if 'delivered_to_mobile' in response:
                        delivered_to_mobile = response['delivered_to_mobile']
                        success_message(request, 'process_transaction',
                            {'transaction':transaction,'status_code': response['status_code'], 'delivered_to_mobile': delivered_to_mobile}
                            )
                    else:
                        error_message(request, 'process_transaction',
                        {'transaction':transaction,'status_code': response['status_code'], 'delivered_to_mobile': delivered_to_mobile}
                        )
                    home_url = request.build_absolute_uri(reverse('home'))
                return TemplateResponse(request, 'redirect_template.html', {'redirect_url':home_url})
            else:


                error_message(request, 'process_transaction',
                    {'status_code': response['status_code']}
                    )
                new_transaction = copy_model_instance(transaction)
                new_transaction.save()

                #wipe the old transaction
                transaction.is_processed = True
                transaction.save()
                #debug(transaction.pk,'old transaction pk')
                #debug(new_transaction.pk,'new transaction pk')
                #return HttpResponseRedirect(reverse('do_cc', args=[new_transaction.get_invoice()]))
                #return redirect(reverse('do_cc', args=[new_transaction.get_invoice()]))
                transaction_url = reverse('do_cc', args=[new_transaction.get_invoice()])
                return TemplateResponse(request, 'redirect_template.html', {'redirect_url':transaction_url})
        else:
            debug(ipay_form.errors, 'Fraud', 'fraud')
        #return HttpResponseRedirect(reverse('do_cc', args=[transaction.get_invoice()]))
        return TemplateResponse(request, 'redirect_template.html', {'redirect_url':transaction_url})

    return render_view(request, 'cc.html', {'process_cc':True,'cc_link':cc_link})


@login_required
def do_cc_madra(request, name):
    '''new cc method'''
    id = int(name) ^ 0xABCDEFAB
    transaction = get_object_or_404(Transaction.objects.filter(id=id, user=request.user,is_processed=False, visa_success=False), id=id, user=request.user, is_processed=False, visa_success=False)

    from payments.cc import prepare_payload
    payload, cc_link = prepare_payload(transaction)
    ipay_url = 'https://ipay.intrepid.co.ke/inm/ipycc.php'
    debug(payload)

    form = doCCForm(initial=payload)

    if request.POST:
        post_values = request.POST.copy()

        try:
            cc_exp = post_values['cc_exp'].replace(' ', '').split("/")
            post_values['cc_exp_month'] = cc_exp[0]
            post_values['cc_number'] = post_values['cc_number'].replace(' ', '')
            if len(cc_exp[1]) > 2:
                post_values['cc_exp_year'] = cc_exp[1][2:]
            else:
                post_values['cc_exp_year'] = cc_exp[1]
        except Exception, e:
            debug(e, 'CC details post error', 'visa')


        form = doCCForm(post_values)

        if form.is_valid():


            response = start_cc(transaction, post_values, request)

            if not response['error']:
                #if visa is successful , do mobile transaction
                response = process_mobilemoney(transaction, response, request)
                try:
                    card_charged_email(request, transaction)
                except Exception, e:
                    debug(e,'sending card charged email','admin')
                delivered_to_mobile = False
                if 'delivered_to_mobile' in response:
                    delivered_to_mobile = response['delivered_to_mobile']
                success_message(request, 'process_transaction',
                    {'status_code': response['status_code'], 'delivered_to_mobile': delivered_to_mobile}
                    )
                return HttpResponseRedirect(reverse('home'))
            else:
                error_message(request, 'process_transaction',
                    {'status_code': response['status_code']}
                    )
        else:
            error_message(request, 'cc_form',
                    {'form_errors': form.errors}
                    )
    return render_view(request, 'do_cc.html',
        {'form':form, 'total_charge':transaction.total_charge, 'countries':COUNTRY_CODES ,'ipay_url':ipay_url})# Create your views here.






from standard.forms import PayPalPaymentsForm

def view_that_asks_for_money(request):

    # What you want the button to do.
    paypal_dict = {
        "business": "mandelashaban593@gmail.com",
        "amount": "10000000.00",
        "item_name": "Donation",
        "invoice": "1",
        "notify_url": "http://www.example.com/your-ipn-location/",
        "return_url": "http://www.example.com/your-return-location/",
        "cancel_return": "http://www.example.com/your-cancel-location/",

    }

    # Create the instance.
    form = PayPalPaymentsForm(initial=paypal_dict)
    context = {"form": form}
   
    return render_to_response("payment.html", context)


