# Create your views here.
from django.template import Template, context, RequestContext
from django.shortcuts import render_to_response, render, \
    get_object_or_404, HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse
#from landingapp.views import *
#from django.contrib.auth.decorators import login_required
from remit.forms import sendMoneyForm, AddToPhonebookForm, PayBillForm, QueryPayBillForm
from remit_admin.forms import  CreateHealthUserForm, AddInfoForm
import remit.settings as settings
# from remit.utils import generate_sha1, mailer, sendsms, error_message, success_message
from remit.utils import error_message, success_message, debug, check_phonebook, get_site_admin, sendsms, check_verified_number, recipient_country_code, COUNTRY_CODE
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from remit.models import Transaction, Phonebook, Wallet, WalletTransaction
from accounts.models import Profile,Create_staff_User, AddInfo
from remit.decorators import ajax_required, login_required
from django.template.loader import render_to_string
import json
from django.db.models import Sum
from django.core.urlresolvers import reverse
import payments.payment as p
from remit.jumio import Jumio
from pesapot.pesapot import PesaPot
from django.contrib import messages




def system_message(request):
    '''this is tmp , implement properly later'''
    msg = 'Due to a system update, all transfers done on January 10, 2015 will be delivered on Sunday January 11, 2015.<br />Sorry for the inconvenience.'
    return {'system_message': False}


def render_view(request, template, data):
    ''' render_view '''
    '''
    wrapper for rendering views , loads RequestContext
    @request  request object
    @template  string
    @data  tumple
    '''
    data.update(access_handler(request))
    data.update(system_message(request))
    if request.user.is_authenticated():
        data.update(userdata(request))
    return render(request,
                  template,
                  data)


def access_handler(request):
    '''verification_handler'''
    data = {}
    if request.user.is_authenticated():
        data['logged_in'] = True
        profile = Profile.objects.get(user=request.user)
        if not profile.id_verified:
            if not profile.userdetails_provided:
                data['provide_userdetails_form'] = True
            elif not profile.id_pic:
                data['upload_id_form'] = True
            elif profile.id_pic and profile.userdetails_provided:
                data['account_verification_in_progress'] = True
        if not profile.email_activated:
            data['email_not_verified'] = True
        if not profile.phone_verified:
            data['phone_not_verified'] = True
        data['USE_JUMIO'] = settings.USE_JUMIO
        data['paybill_enabled'] = False
        if settings.PAYBILL and profile.send_country_code == '256':
            data['paybill_enabled'] = settings.PAYBILL
    return data


def userdata(request):
    '''add user data'''
    profile = Profile.objects.get(user=request.user)
    userdata = {}
    if profile.id_verified:
        transaction_stats = Transaction.objects.filter(
            user=profile.user, visa_success=True, is_processed=True,
            amount_sent__isnull=False)
        userdata['profile_successful_transactions'] = transaction_stats.count()
        if userdata['profile_successful_transactions'] > 0:
            userdata['profile_amount_sent'] = transaction_stats.aggregate(
                Sum('amount_sent'))
            if 'amount_sent__sum' in userdata['profile_amount_sent']:
                userdata['profile_amount_sent'] = userdata[
                    'profile_amount_sent']['amount_sent__sum']
            pending_transactions = Transaction.objects.filter(
                user=profile.user,
                visa_success=True,
                is_processed=False,
                amount_sent__isnull=False
            )
            userdata['pending_transactions'] = pending_transactions
        else:
            userdata['successful_transactions'] = '0'
    return userdata


def save_to_phonebook(data, user):
    '''save phonenumber to phonebook'''
    pb = {}
    pb['lastname'] = data['receiver_lname']
    pb['firstname'] = data['receiver_fname']
    pb['ext'] = data['phonenumber_ext']
    pb['number'] = data['receiver_number']
    pb['user'] = user.pk
    pb['country_code'] = data['phonenumber_ctry']
    pbform = AddToPhonebookForm(pb)
    if pbform.is_valid():
        # check if the phonenumber exists
        check_number = check_phonebook(pb)
        if not check_number:
            try:
                pbform.save()
            except Exception, e:
                debug(e, 'phonenumber save error', 'admin')
                pass


@login_required
def wallet(request):
    ewallet = get_object_or_404(
        Wallet.objects.filter(user=request.user),
        user=request.user
        )
    transactions = ewallet.transactions
    if request.POST:
        rechargeamount = request.POST.get('rechargeamount', None)
        if rechargeamount:
            transaction = Transaction(
                user=request.user,
                amount_sent=rechargeamount,
                from_wallet=ewallet
                )
            transaction = transaction.save()
            if transaction:
                rechargeamount = float(rechargeamount)
                wallettransaction = WalletTransaction(
                wallet=ewallet,
                transaction=transaction,
                added_by=request.user,
                amount=rechargeamount
                ).save()
                return HttpResponseRedirect(reverse('do_cc',
                                                        args=[
                                                            transaction.get_invoice()]
                                                        ))

    return render_view(request, 'wallet.html', {
        'wallet': ewallet,
        'transactions': transactions
        })


@login_required
def home_page(request, country=False):
    '''
    handles the home page
    @request  request object
    '''
    profile = Profile.objects.get(user=request.user)
    phonebook = None
    jumio_auth_token = "abc"
    jumio_ref_id = "ref_id"



    if profile.verification_attempts > 0:
        #
        # get jumio auth token
        response_data = {}
        jumio = Jumio()
        #auth_token = jumio.auth_token()
        jumio_data = jumio.auth_token()
        jumio_auth_token = jumio_data['auth_token']
        jumio_ref_id = jumio_data['scan_ref']

        profile.id_scan_ref = jumio_ref_id
        profile.save()

        #print 'home page jumio auth: ', str(jumio_auth_token)

    if profile.id_verified:
        country_code = False
        extradata = {}
        if 'extradata' in request.session:
            extradata = request.session['extradata']
            country_code = extradata['ext']
            country = 1
            del request.session['extradata']

        if country:
            try:
                country_code = COUNTRY_CODE[country]
            except Exception, e:
                pass
        else:
            country_code = recipient_country_code(request, remove_session=True)

        if country_code:
            profile.send_country_code = country_code
            profile.save()
        else:
            country_code = profile.send_country_code

        if request.POST:

            # if the user wants to save to phonebook we do that
            if request.POST.get('save_to_phonebook', False):
                try:
                    save_to_phonebook(request.POST, request.user)
                except Exception, e:
                    debug(e, 'phonenumber save error', 'admin')

            post_values = request.POST.copy()
            post_values['user'] = request.user.pk
            post_values['receiver_country_code'] = country_code

            try:
                post_values['receiver_number'] = '%s%s' % (post_values.get(
                    'phonenumber_ext', False), post_values['receiver_number'])
            except Exception, e:
                pass

            default_error_msg = 'An error occurred while trying to process your transaction, please try again. If the transaction fails please contact our support team'

            form = sendMoneyForm(post_values)
            if form.is_valid():
                transaction = form.save()

                if transaction:
                    return HttpResponseRedirect(reverse('do_cc',
                                                        args=[
                                                            transaction.get_invoice()]
                                                        ))
                else:
                    error_message(
                        request, 'sendmoney', {'errors': default_error_msg})
            else:
                error_message(request, 'sendmoney', {
                              'errors': default_error_msg})

    """
    elif not profile.id_verified:
        #
        response_data={}
        jumio = Jumio()
        #auth_token = jumio.auth_token()
        jumio_data = jumio.auth_token()
        jumio_auth_token = jumio_data['auth_token']
        jumio_ref_id = jumio_data['scan_ref']
    """

    rate = profile.current_rate()
    phonextensions = rate.extra_fees

    phonebook = Phonebook.objects.all().filter(user=request.user.pk,
                                               country_code=profile.send_country_code)
    phonenumbers = []
    # if hasattr(phonebook, '__contains__'):
    if phonebook:
        for number in phonebook:
            phonenumbers.append(number.phonenumber_with_countrycode())
    extradata = {}
    if 'extradata' in request.session:
        extradata = request.session['extradata']

        del request.session['extradata']

    return render_view(request, 'home.html', {
        'phonebook': phonebook,
        'phonenumbers': phonenumbers,
        'extradata': extradata, 'OTHER_FEES': settings.OTHER_FEES,
        'phonextensions': phonextensions,
        'rate': rate,
        'jumio_auth_token': jumio_auth_token
    }
    )


def ipay_hash(p):
    import hmac
    import hashlib
    data = '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s' % (
        p['live'], p['mm'], p['mb'], p['dc'], p['cc'], p['mer'], p[
            'oid'], p['inv'], p['ttl'], p['tel'], p['eml'], p['vid'],
        p['cur'], p['p1'], p['p2'], p['p3'], p['p4'], p['cbk'], p['cst'], p['crl'])
    hash_key = hmac.new(settings.IPAY_HASH_KEY, data, hashlib.sha1).hexdigest()
    return hash_key


@login_required
def confirm_payment(request):
    '''
    handles the signup page
    @request  request object
    '''
    if p.check_source(request):
        response = p.process_transaction(request)
        if not response['error']:
            delivered_to_mobile = False
            if 'delivered_to_mobile' in response:
                delivered_to_mobile = response['delivered_to_mobile']
            success_message(request, 'process_transaction', {
                            'status_code': response['status_code'], 'delivered_to_mobile': delivered_to_mobile})
        # add scenarios incase card charged and users money not sent
        else:
            error_message(request, 'process_transaction', {
                          'status_code': response['status_code']})
        # return HttpResponseRedirect(reverse('home'))
        return TemplateResponse(request, 'redirect_template.html', {'redirect_url': reverse('home')})
    else:
        p.log_fraud(request)
    return HttpResponseRedirect(reverse('custom_404'))


@login_required
def transactions(request):
    '''
    handles the signup page
    @request  request object
    '''
    transactions_list = Transaction.objects.all().filter(
        visa_success=True,
        # is_processed=True,
        amount_sent__isnull=False,
        user=request.user
    ).order_by('-id')

    pending = len(transactions_list.filter(is_processed=False))

    paginator = Paginator(transactions_list, settings.PAGNATION_LIMIT)
    page = request.GET.get('page')
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        transactions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        transactions = paginator.page(paginator.num_pages)
    return render_view(request, 'transactions.html', {'transactions': transactions, 'pending': pending})


@login_required
def pending_transactions(request):
    '''
    handles the signup page
    @request  request object
    '''
    transactions_list = Transaction.objects.all().filter(
        visa_success=True, is_processed=False, amount_sent__isnull=False, user=request.user).order_by('-id')
    paginator = Paginator(transactions_list, settings.PAGNATION_LIMIT)
    page = request.GET.get('page')
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        transactions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        transactions = paginator.page(paginator.num_pages)
    return render_view(request, 'pending_transactions.html', {'transactions': transactions})


@login_required
def transaction(request, name):
    id = int(name) ^ 0xABCDEFAB
    transaction = get_object_or_404(Transaction.objects.filter(
        id=id, user=request.user), id=id, user=request.user)
    return render_view(request, 'transaction.html', {'transaction': transaction})


@login_required
def phonebook(request):
    '''
    handles the signup page
    @request  request object
    '''
    phonebooks_list = Phonebook.objects.all().filter(
        user=request.user.pk).order_by('firstname')
    paginator = Paginator(phonebooks_list, settings.PAGNATION_LIMIT)
    page = request.GET.get('page')
    try:
        phonebook = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        phonebook = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        phonebook = paginator.page(paginator.num_pages)
    return render_view(request, 'phonebook.html', {'phonebook': phonebook})


@ajax_required
def delete_from_phonebook(request):
    template = settings.AJAX_TEMPLATE_DIR + 'delete_from_phonebook.html'
    phonebook = response = False
    if request.POST:
        if 'uid' in request.POST:
            id = request.POST['uid']
            try:
                phonebook = Phonebook.objects.get(user=request.user.pk, id=id)
            except Exception, e:
                print e
            if phonebook:
                phonebook.delete()
                response = True
    html = render_to_string(template, {'response': response})
    return HttpResponse(html)


@ajax_required
def add_to_phonebook(request):
    template = settings.AJAX_TEMPLATE_DIR + 'add_to_phonebook.html'
    response = False
    post_values = {}
    if request.POST:
        post_values = request.POST.copy()
        post_values['user'] = request.user.pk
        form = AddToPhonebookForm(post_values)
        if form.is_valid():
            try:
                check_phonebook = check_phonebook(post_values)
                response = False
                post_values['duplicate'] = True
            except Exception:
                form.save()
                response = True
        else:
            print form.errors
    html = render_to_string(
        template, {'response': response, 'data': post_values})
    return HttpResponse(html)


@ajax_required
def edit_phonebook(request):
    template = settings.AJAX_TEMPLATE_DIR + 'edit_phonebook.html'
    response = False
    if request.POST:
        phonebook = value = False
        id = request.POST['elementid']
        if 'value' in request.POST:
            value = request.POST['value']
        try:
            phonebook = Phonebook.objects.get(id=id, user=request.user.pk)
        except Exception, e:
            pass
        if phonebook and value:
            if request.POST['option'] == 'lastname':
                phonebook.lastname = value
            if request.POST['option'] == 'firstname':
                phonebook.firstname = value
            phonebook.save()
    return HttpResponse(request.POST['value'])


@login_required
@ajax_required
def ajax_server(request):
    '''
    handles the signup page
    @request  request object
    '''

    '''check phonebook'''
    response = {}
    data = {}
    if 'check_phonebook' in request.GET:
        response = {'show': False}
        phonebook = False
        try:
            data['user'] = request.user.pk
            data['number'] = request.GET['number']
            data['ext'] = request.GET['ext']
            data['country_code'] = request.GET['country_code']
            phonebook = check_phonebook(data)
        except Exception:
            pass
        if not phonebook:
            response['show'] = True

    if 'is_verified' in request.GET:
        try:
            data['ext'] = request.GET['ext']
            data['number'] = request.GET['number']
            data['country_code'] = request.GET['country_code']
            number = '%s%s' % (data['ext'], data['number'])
            response = check_verified_number(
                request, number, request.user.email)
        except Exception, e:
            debug(e)

    if 'querypaybill' in request.GET:
        try:
            data['location'] = request.GET['location']
            data['referencenumber'] = request.GET['referencenumber']
            data['billtype'] = request.GET['billtype']
            form = QueryPayBillForm(data)
            if form.is_valid():
                pesapot = PesaPot()
                response = pesapot.QueryPayBillAccount(
                    referencenumber=data.get('referencenumber'),
                    billtype=data.get('billtype'),
                    location=data.get('location')
                )
            else:
                response = form.errors
        except Exception, e:
            debug(e)

    if 'json' in request.GET:
        return HttpResponse(json.dumps(response),
                            content_type="application/json")
    return HttpResponse(response)


def custom_404(request):
    '''
    404 page
    @request  request object
    '''
    return handler404(request)


def custom_403(request):
    '''
    404 page
    @request  request object
    '''
    return handler403(request)


def custom_503(request):
    '''
    503 page
    @request  request object
    '''
    return handler500(request)


def handler404(request):
    response = render_to_response('my404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('my500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response


def handler403(request):
    response = render_to_response('my500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 403
    return response


def csrf_failure_view(request, reason):
    '''csrf_failure_view'''
    debug(reason, 'csrf_failure', 'csrf_failure')
    response = render_to_response('csrf_failure.html', {},
                                  context_instance=RequestContext(request))
    return response


#@login_required
def restricted_media_view(request, image):
    '''restrict image view to particular people'''
    if request.user.is_authenticated():
        if request.user.is_superuser or request.user.is_staff:
            pass
        else:
            id_pic = str(request.user.profile.id_pic)
            filename = id_pic.split('/')[-1]
            if not filename == image:
                return HttpResponseRedirect(reverse('custom_404'))
        import mimetypes
        import os
        import stat
        from django.utils.http import http_date
        from django.http import StreamingHttpResponse
        fullpath = "%s/uploads/images/uploads/%s" % (
            settings.STATIC_ROOT, image)
        if not os.path.exists(fullpath):
            return HttpResponseRedirect(reverse('custom_404'))
        statobj = os.stat(fullpath)
        content_type, encoding = mimetypes.guess_type(fullpath)
        content_type = content_type or 'application/octet-stream'
        response = StreamingHttpResponse(open(fullpath, 'rb'),
                                         content_type=content_type)
        response["Last-Modified"] = http_date(statobj.st_mtime)
        if stat.S_ISREG(statobj.st_mode):
            response["Content-Length"] = statobj.st_size
        if encoding:
            response["Content-Encoding"] = encoding
        return response
    else:
        return HttpResponseRedirect(reverse('custom_404'))


def verification(request):
    return render_view(request,
                       'verification.html', {}
                       )


@login_required
def paybill(request):
    profile = Profile.objects.get(
        user=request.user
    )
    if not profile.send_country_code == '256':
        return HttpResponseRedirect(reverse('custom_404'))
    rate = profile.current_rate()
    form = QueryPayBillForm()
    confirm = None
    response = {}
    result = {}
    referencenumber = None
    amount_received = None
    amount_sent = None
    charge = None
    billtype = None
    numbilltype = None
    location = None
    utility_account_type = None

    if request.POST:
        data = request.POST.copy()
        confirm = data.get('confirm', None)
        if not confirm:
            form = QueryPayBillForm(data)
            if form.is_valid():
                referencenumber = data.get('referencenumber')
                charge = data.get('amount_charged')
                amount_sent = data.get('amount')
                billtype = data.get('billtype')
                billtype = int(billtype)
                numbilltype = billtype
                location = data.get('location')
                amount_received = data.get('amount_received', None)
                #print 'Amount recieved: ',str(amount_received);
                pesapot = PesaPot()
                response = pesapot.QueryPayBillAccount(
                    referencenumber=referencenumber,
                    billtype=billtype,
                    location=location
                )
                result = response.get('result', {})
                responsecode = response.get('responsecode', 0)


                account_name = response.get('result',{}).get('customer_name','')
                request.session['account_name'] = "".join(account_name.split())


                utility_account_type = response.get('result',{}).get('customer_type','')

                if utility_account_type == None or utility_account_type == '':
                    request.session['utility_account_type'] = 'POSTPAID'
                else:
                    request.session['utility_account_type'] = utility_account_type


                responsecode = int(responsecode)
                if billtype == 1:
                    billtype = 'Electricity (UMEME)'
                else:
                    billtype = 'Water (NWSC)'
                if responsecode == 8:
                    messages.error(request,
                                   "The Service is currently unavailable"
                                   )
                elif 'errors' in response:
                    if responsecode == 7 or responsecode == 8:
                        edata = {}
                        edata['referencenumber'] = referencenumber
                        edata['billtype'] = billtype
                        error_message(request, 'paybill', edata)
                elif 'status_code' in result:
                    if result['status_code'] == '0' or 'customer_name' in result:
                        confirm = True
                        form = PayBillForm()
        else:
            result = response.get('result', {})
            data['receiver_country_code'] = 256
            data['utility'] = True
            data['user'] = request.user.pk
            data['billtype'] = data.get('numbilltype')
            data['billarea'] = data.get('billarea', 'Kampala')
            #data['amount_received'] = self.amount_received
            number = "%s%s" % (
                data['phonenumber_ext'],
                data['receiver_number']
                )
            data['receiver_number'] = number
            #data['utility_account_name']=account_name
            #

            data['utility_account_name']=request.session['account_name']

            data['utility_account_type']=request.session['utility_account_type']

            data['amount_received'] = data.get('amount_received', None)


            #print ':View amount recieved: ',str(data['amount_received'])
            form = PayBillForm(data)
            #print ':Form result: ',str(form)
            if form.is_valid():
                transaction = form.save()

                if transaction:
                    return HttpResponseRedirect(reverse('do_cc',
                                                        args=[
                                                            transaction.get_invoice()]
                                                        ))
                else:
                    default_error_msg = 'An error occurred while trying to process your transaction, please try again. If the transaction fails please contact our support team'
                    error_message(
                        request, 'sendmoney', {'errors': default_error_msg})
    return render_view(request,
                       'paybill.html', {
                           'response': response,
                           'referencenumber': referencenumber,
                           'accountbalance': result.get('oustanding_balance'),
                           'customer_name': result.get('customer_name'),
                           'rate': rate,
                           'form': form,
                           'confirm': confirm,
                           'amount_received': amount_received,
                           'amount_sent': amount_sent,
                           'charge': charge,
                           'billtype': billtype,
                           'numbilltype': numbilltype,
                           'phonextensions': rate.extra_fees,
                           'location': location
                       }
                       )



def clinics(request):
    '''
    E-consult
    @request  request object
    '''
    return render_view(request, 'clinics.html', {})






def Create_staff_User(request, is_customer_care=False):
    '''create an admin user'''
    form = CreateHealthUserForm()
    add_info = AddInfoForm()

    if request.POST:
        form = CreateHealthUserForm(request.POST)
        if form.is_valid():

            user = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password'])
            user.save()
            user.is_staff = True
            user.save()
            profile = AdminProfile(user=user)
            profile.save()
            user = Create_staff_User(user=user, username=form.cleaned_data['username'],email=form.cleaned_data['email'],category=form.cleaned_data['category'],cat_name=form.cleaned_data['cat_name'],doct_name=form.cleaned_data['doct_name'],role=form.cleaned_data['role'],password=form.cleaned_data['password'],phone=form.cleaned_data['phone'],region=form.cleaned_data['region'],districts=form.cleaned_data['districts'], info=form.cleaned_data['info'])

            user.save()
            
            # user.save()
            # assign user permissions
            update = False
        
            messages.success(request, "The User Was Successfully Created")
    return render_view(request, 'create_health_user.html', {'form': form, 'add_info':add_info}
                       )


