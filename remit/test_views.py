'''Test views'''
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from remit.forms import doCCForm
from remit.utils import debug, success_message, error_message
from remit.models import Transaction
from django.contrib import messages
from remit.cc import start_cc
from remit.decorators import login_required
from remit.payment import process_mobilemoney, card_charged_email
from remit.misc import COUNTRY_CODES
from django.core.urlresolvers import reverse

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

@login_required
def do_cc(request, name):
    '''new cc method'''
    id = int(name) ^ 0xABCDEFAB
    transaction = get_object_or_404(Transaction.objects.filter(id=id, user=request.user,is_processed=False, visa_success=False), id=id, user=request.user, is_processed=False, visa_success=False)
    form = doCCForm()
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
            
            #Do visa transaction
            response = start_cc(transaction, post_values)

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
            #messages.error(request,'Please provide the correct CC details, %s' % form.errors )
            error_message(request, 'cc_form', 
                    {'form_errors': form.errors}
                    )
    return render_view(request, 'do_cc.html', 
        {'form':form, 'total_charge':transaction.total_charge, 'countries':COUNTRY_CODES })