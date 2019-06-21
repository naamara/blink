


 
 
 
    
    
    
                   'subscr_date', 'subscr_effective')
            #When commit = False, object is returned without saving to DB.
            del data[date_field]
            flag = "Exception while processing. (%s)" % e
            ipn_obj = form.save(commit = False)
            ipn_obj.verify(item_check_callable)
            ipn_obj.verify_secret(form, request.GET['secret'])
        # Secrets should only be used over SSL.
        #We save errors in the flag field
        else:
        except Exception, e:
        flag = "Invalid form. (%s)" % form.errors
        if data.get(date_field) == 'N/A':
        if request.is_secure() and 'secret' in request.GET:
        ipn_obj = PayPalIPN()
        ipn_obj.set_flag(flag)
        try:
    """
    """
    #      of if checks just to determine if flag is set.
    # Clean up the data as PayPal sends some weird values such as "N/A"
    #Set query params and sender's IP address
    #TODO: Clean up code so that we don't need to set None here and have a lot
    data = request.POST.copy()
    date_fields = ('time_created', 'payment_date', 'next_payment_date',
    else:
    else:
    flag = None
    for date_field in date_fields:
    form = PayPalIPNForm(data)
    http://tinyurl.com/d9vu9d
    https://developer.paypal.com/cgi-bin/devscr?cmd=_ipn-link-session
    if flag is not None:
    if form.is_valid():
    if ipn_obj is None:
    ipn_obj = None
    ipn_obj.initialize(request)
    ipn_obj.save()
    PayPal IPN endpoint (notify_url).
    PayPal IPN Simulator:
    return HttpResponse("OKAY")
    Used by both PayPal Payments Pro and Payments Standard to confirm transactions.
# -*- coding: utf-8 -*-
#!/usr/bin/env python
@csrf_exempt
@require_POST
def ipn(request, item_check_callable=None):
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ipn.forms import PayPalIPNForm
from ipn.models import PayPalIPN