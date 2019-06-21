# Create your views here.
from django.template import Template, context, RequestContext
from django.shortcuts import render_to_response, render, get_object_or_404, redirect, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from remit_admin.forms import RateUpdateForm, ProfileUpdateForm, ProfileAddForm, PhonebookAddForm, TransactionAddForm, CreateAdminUserForm, TransactionUpdateForm, ContactUserForm, EditAdminUserForm, transactionPhonenumberSearchForm, ChargesLimitsForm,CreateHealthUserForm,AddInfoForm,AddHealthInfoForm,AddLawInfoForm,AddPubInfoForm,AddEducInfoForm
import remit.settings as settings
#from remit.utils import generate_sha1, mailer, sendsms, error_message, success_message
from remit.utils import error_message, success_message, admin_mail, sendsms, mailer
import payments.payment as p
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from remit.models import Transaction, Phonebook, Rate, Country, Charge
from remit.utils import COUNTRY_CHOICES, NETWORK_CHOICES
from accounts.models import Profile, AdminProfile, UserActions,Create_staff_User
from remit_admin.decorators import admin_required, superuser_required, permission_required, customer_care_required
from django.db.models import Q
from datetime import datetime,  timedelta
import payments.payment as payments
from django.db.models import Sum, Max
from django.contrib import messages
from django.db import IntegrityError
import remit_admin.utils as admin_utils
import urllib2
from django.core.files.base import ContentFile
from StringIO import StringIO
from PIL import Image
from remit.utils import debug, log_unauthorized_access, render_to_pdf
#from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from remit_admin.models import EmailSupport, add_health_info,HealthInfo,LawhInfo,JounalisthInfo,EducationInfo


import pytz
from django.contrib.auth.models import User
from remit_admin.utils import log_action, store_login_info
from pesapot.pesapot import PesaPot


def dashboard_stats(request):
    '''Data for the admin templated'''
    data = {'boss_man': False}
    countries = Country.objects.all()
    if request.user.is_active and request.user.is_staff:
        '''get data only when user is logged in'''

        profile = User.objects.filter(
            is_superuser=False, is_staff=False).count()
        data['user_count'] = profile

        data['verified_user_count'] = admin_utils.verified_users(
            count=True)

        data['blocked_user_count'] = admin_utils.blocked_users(count=True)

        data['pending_user_count'] = admin_utils.users_pending_verification(
            count=True)

        transaction = Transaction.objects.filter(
            visa_success=True, is_processed=False, amount_sent__isnull=False).aggregate(Sum('amount_sent'))
        data['amount_pending'] = transaction['amount_sent__sum']

        for country in countries:
            currency = country.currency.lower()
            # amount pending
            transaction = Transaction.objects.filter(
                visa_success=True, is_processed=False, to_country=country.pk, amount_sent__isnull=False).aggregate(Sum('amount_received'))
            data['amount_pending_%s' % currency] = transaction[
                'amount_received__sum']
            # pending transactions
            transaction = Transaction.objects.filter(
                visa_success=True, is_processed=False, amount_sent__isnull=False, to_country=country.pk).count()

            data['pending_transactions_%s' % currency] = transaction

        data['pending_transactions'] = len(Transaction.momo.pending())

        transaction = Transaction.objects.filter(
            visa_success=False, is_processed=False, amount_sent__isnull=False).count()
        data['failed_transactions'] = transaction

        transaction = Transaction.objects.filter(
            visa_success=True, is_processed=True, amount_sent__isnull=False).aggregate(Sum('amount_sent'))
        data['total_amount_transfered'] = transaction['amount_sent__sum']

        transaction = Transaction.objects.filter(
            visa_success=True, is_processed=True, amount_sent__isnull=False).aggregate(Sum('amount_sent'))
        data['total_amount_transfered'] = transaction['amount_sent__sum']

        transaction = Transaction.objects.filter(
            visa_success=True, is_processed=True, amount_sent__isnull=False).aggregate(Sum('amount_received'))
        data['total_amount_transfered_ugx'] = transaction[
            'amount_received__sum']

        data['user_with_transaction'] = Transaction.objects.filter(
            visa_success=True, is_processed=True, amount_sent__isnull=False).values('user').distinct().count()
        data['complete_transactions'] = Transaction.objects.filter(
            visa_success=True, is_processed=True, amount_sent__isnull=False).count()

        data['pending_bills'] = Transaction.objects.filter(
            visa_success=True,
            is_processed=False,
            amount_sent__isnull=False,
            utility=True
        ).count()

        data['cancelled_bills'] = Transaction.objects.filter(
            visa_success=True,
            is_processed=False,
            amount_sent__isnull=False,
            utility=True
        ).count()

        data['failed_bills'] = Transaction.objects.filter(
            visa_success=False,
            is_processed=False,
            amount_sent__isnull=False,
            utility=True
        ).count()
    return data


@admin_required
def render_view(request, template, data):
    '''
    wrapper for rendering views , loads RequestContext
    @request  request object
    @template  string
    @data  tumple
    '''

    # store login info
    if not 'login_info' in request.session:
        store_login_info(request)
        # debug(request.session['login_info'])

    # user permissions
    if request.user.is_authenticated():
        permissions = get_user_permissions(request.user)
        profile = {}
        try:
            profile = AdminProfile.objects.get(user=request.user)
        except Exception, e:
            if request.user.is_superuser:
                create_superuser(request.user)
        data.update({'profile': profile, 'permissions': permissions})
    # for pagnation
    #debug(permissions, 'permissions')
    queries_without_page = request.GET.copy()
    if queries_without_page.has_key('page'):
        del queries_without_page['page']
    # update the request context
    data.update(
        {'queries': queries_without_page})
    data.update({'admin_data': dashboard_stats(request)})
    return render_to_response(
        template, data,
        context_instance=RequestContext(request)
    )


def create_superuser(user):
    '''we are not doing this'''
    profile = AdminProfile.objects.create(user=user)


def get_user_permissions(user):
    '''return user permissions as a dict'''
    permissions = {}
    for x in Permission.objects.filter(user=user):
        permissions.update({x.codename: True})
    return permissions


def get_country_access(user):
    '''get the users country access'''
    countries = ()
    if user.is_superuser:
        countries = COUNTRY_CHOICES
    else:
        profile = AdminProfile.objects.get(user=user)
        if not profile.country == 'False':
            for keyword, value in COUNTRY_CHOICES:
                if profile.country == keyword:
                    countries = ((keyword, value),)
        else:
            countries = COUNTRY_CHOICES
    return countries


def get_network_access(user):
    '''get the users network access'''
    networks = {}
    if user.is_superuser:
        networks = NETWORK_CHOICES
    else:
        profile = AdminProfile.objects.get(user=user)
        if not profile.mobile_network == 'False':
            networks = profile.mobile_network
            for keyword, value in NETWORK_CHOICES:
                if profile.mobile_network == keyword:
                    networks = ((keyword, value),)
        else:
            networks = NETWORK_CHOICES
    return networks


def check_user_permission(user, codename):
    '''check if user has a particular permission to do something'''
    if user.is_superuser:
        # Admin is all powerfull
        return True
    else:
        perm = Permission.objects.filter(user=user, codename=codename)
        return perm


@admin_required
def home(request):
    print "Everythin is fine"
    ad = AdminProfile.objects.get(user=request.user)
    if request.user.is_superuser:
        countries = Country.objects.all()
        return render_view(request, 'admin/index.html', {'countries': countries})

    elif ad.is_lawyer == True:
        print "Everythin is fine"
        return render_view(request, 'admin/index_staff_lawyer.html', {})
    elif ad.is_educ == True:
        print "Everythin is fine"
        return render_view(request, 'admin/index_staff_educ.html', {})

    elif ad.is_doctor == True:
        print "Everythin is fine"
        return render_view(request, 'admin/index_staff_doctor.html', {})

    elif ad.is_jounalist == True:
        print "Everythin is fine"
        return render_view(request, 'admin/index_staff_jounalist.html', {})

    else:
        return render_view(request, 'admin/index_staff.html', {})


@permission_required('edit_user')
def unblock_user(request):
    '''
    block user
    admin is responsible for all the nastiness
    '''
    if request.POST:
        if not 'unblock_user' in request.POST:
            return HttpResponseRedirect(reverse('custom_404'))
            # print request.POST
        else:
            id = int(request.POST['unblock_user']) ^ 0xABCDEFAB
            '''check if the user is waiting verification'''
            profile = get_object_or_404(Profile.objects.filter(
                id=id, account_blocked=True), id=id, account_blocked=True)

            ''' Block user '''
            profile.unblocked_by = request.user
            profile.status_updated_on = datetime.now()
            profile.account_blocked = False
            try:
                profile.save()
                success_message(
                    request, 'admin_user_unblocked', {'profile': profile})

                # account verified email and sms
                # template = settings.EMAIL_TEMPLATE_DIR+'general.html'
                # c ={'admin_user_unverified': True, 'data':profile}
                # mailer(request, 'VERIFIED: Your identity has been verified', template, c, profile.user.email)

                # send sms
                # template = settings.SMS_TEMPLATE_DIR+'general.html';
                # sendsms(profile.get_phonenumber(),template,{'code':'admin_user_verified','profile':profile})

            except Exception, e:
                error_message(
                    request, 'admin_user_unblocked', {'profile': profile})
                admin_mail(request, 'server_error', {
                           'error_message': 'errror unverifying user'}, e)
    # return HttpResponseRedirect(settings.BASE_URL + 'admin/users/verified/')
    return HttpResponseRedirect(reverse('admin:admin_users', args=['verified']))


@superuser_required
def block_user(request):
    '''
    block user
    admin is responsible for all the nastiness
    '''
    if request.POST:
        if not 'block_user' in request.POST:
            return HttpResponseRedirect(reverse('custom_404'))
            # print request.POST
        else:
            id = int(request.POST['block_user']) ^ 0xABCDEFAB
            '''check if the user is waiting verification'''
            profile = get_object_or_404(Profile.objects.filter(id=id), id=id)

            ''' Block user '''
            profile.blocked_by = request.user
            profile.status_updated_on = datetime.now()
            profile.account_blocked = True
            try:
                profile.save()
                log_action(request, model_object=profile,
                           action_flag=15, change_message='blocked user')
                success_message(
                    request, 'admin_user_blocked', {'profile': profile})

                # account verified email and sms
                # template = settings.EMAIL_TEMPLATE_DIR+'general.html'
                # c ={'admin_user_unverified': True, 'data':profile}
                # mailer(request, 'VERIFIED: Your identity has been verified', template, c, profile.user.email)

                # send sms
                # template = settings.SMS_TEMPLATE_DIR+'general.html';
                # sendsms(profile.get_phonenumber(),template,{'code':'admin_user_verified','profile':profile})

            except Exception, e:
                error_message(
                    request, 'admin_user_blocked', {'profile': profile})
                admin_mail(request, 'server_error', {
                           'error_message': 'errror unverifying user'}, e)
    # return HttpResponseRedirect(settings.BASE_URL + 'admin/users/verified/')
    return HttpResponseRedirect(reverse('admin:admin_users', args=['verified']))


@superuser_required
def unverify_user(request):
    '''
    unverify user
    admin is responsible for all the nastiness
    '''
    if request.POST:
        if not 'unverifyuser' in request.POST:
            return HttpResponseRedirect(reverse('custom_404'))
            # print request.POST
        else:
            id = int(request.POST['unverifyuser']) ^ 0xABCDEFAB
            '''check if the user is waiting verification'''
            profile = get_object_or_404(Profile.objects.filter(
                id=id, account_verified=True, id_verified=True, user__isnull=False), id=id, account_verified=True, id_verified=True, user__isnull=False)

            ''' verify user '''
            profile.unverified_by = request.user
            profile.status_updated_on = datetime.now()
            profile.account_verified = False
            profile.id_verified = False
            try:
                profile.save()
                success_message(
                    request, 'admin_user_unverified', {'profile': profile})

                # account verified email and sms
                # template = settings.EMAIL_TEMPLATE_DIR+'general.html'
                # c ={'admin_user_unverified': True, 'data':profile}
                # mailer(request, 'VERIFIED: Your identity has been verified', template, c, profile.user.email)

                # send sms
                # template = settings.SMS_TEMPLATE_DIR+'general.html';
                # sendsms(profile.get_phonenumber(),template,{'code':'admin_user_verified','profile':profile})

            except Exception, e:
                error_message(
                    request, 'admin_user_unverified', {'profile': profile})
                admin_mail(request, 'server_error', {
                           'error_message': 'errror unverifying user'}, e)
    # return HttpResponseRedirect(settings.BASE_URL + 'admin/users/verified/')
    return HttpResponseRedirect(reverse('admin:admin_users', args=['verified']))


@superuser_required
def verify_user(request):
    '''
    verify user
    admin is responsible for all the nastiness
    '''
    if request.POST:
        if not 'verifyuser' in request.POST:
            return HttpResponseRedirect(reverse('custom_404'))
        else:
            id = int(request.POST['verifyuser']) ^ 0xABCDEFAB
            '''check if the user is waiting verification'''
            profile = get_object_or_404(
                Profile.objects.filter(
                    id=id, account_verified=False, id_pic__isnull=False, id_verified=False,
                    account_blocked=False), id=id, account_verified=False, id_pic__isnull=False, id_verified=False, account_blocked=False)

            ''' verify user '''
            profile.verified_by = request.user
            profile.status_updated_on = datetime.now()
            profile.account_verified = True
            profile.id_verified = True
            try:
                profile.save()
                log_action(request, model_object=profile,
                           action_flag=9, change_message='verified user')
                success_message(
                    request, 'admin_user_verified', {'profile': profile})
                # account verified email and sms
                template = settings.EMAIL_TEMPLATE_DIR + 'general.html'
                user_email = profile.user.email
                user_names = profile.get_names()

                c = {'admin_user_verified': True, 'user_names': user_names}
                mailer(request, 'VERIFIED: Your account on %s has been verified' % settings.APP_NAME,
                       template, c, user_email)

                # send sms
                if profile.phone_verified:
                    template = settings.SMS_TEMPLATE_DIR + 'general.html'
                    sendsms(profile.get_phonenumber(), template, {
                            'code': 'admin_user_verified', 'user_names': user_names})
            except Exception, e:
                debug(e, 'error sending verification emails ')
                admin_mail(request, 'server_error', {
                           'error_message': 'errror verifying user : %s' % e}, e)
    return HttpResponseRedirect(reverse('admin:admin_users', args=['pending_verification']))


@permission_required('view_transaction')
def view_transaction(request, name):
    name = int(name) ^ 0xABCDEFAB
    transaction = get_object_or_404(Transaction.objects.filter(pk=name))

    log_action(request, model_object=transaction, action_flag=6,
               change_message='Viewed Transaction')

    return render_view(request, 'admin/transaction.html',
                       {'transaction': transaction})


@superuser_required
def resend_transaction_email(request, name):
    pk = int(name) ^ 0xABCDEFAB
    transaction = get_object_or_404(Transaction.objects.filter(pk=pk))
    if request.POST:
        from payments.payment import card_charged_email, transaction_delivered_email
        email = transaction.user.email
        action = request.POST.get('action', None)
        if action == '2':
            action = "Card Charged Email"
            card_charged_email(request, transaction)
        if action == '1':
            action = "Delivery Email"
            transaction_delivered_email(request, transaction)
        log_action(request, model_object=transaction, action_flag=6,
                   change_message='Resend Transaction Email')
        messages.success(
            request, "The %s email Was Successfully resent to %s" % (action, email))
    return HttpResponseRedirect(reverse('admin:admin_transaction', args=(name,)))


def transaction_receipt(request, name):
    name = int(name) ^ 0xABCDEFAB
    transaction = get_object_or_404(Transaction.objects.filter(pk=name))
    template = settings.EMAIL_TEMPLATE_DIR + 'credit_card_charged_pdf.html'
    #log_action(request,model_object=transaction, action_flag=6, change_message='Downloaded Receipt Transaction')
    return render_to_pdf(
        template, {
            'data': transaction,
            'BASE_URL': settings.BASE_URL
        }
    )


@superuser_required
def edit_transaction(request, name):
    name = int(name) ^ 0xABCDEFAB
    transaction = get_object_or_404(Transaction.objects.filter(pk=name))
    form = TransactionUpdateForm()
    if request.POST:
        form = TransactionUpdateForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            transaction.updated_by = request.user
            transaction.save()
            success_message(request, 'admin_edit_transaction', {})
            admin_mail(request, 'transaction_updated',
                       {'transaction': transaction})
            log_action(request, model_object=transaction,
                       action_flag=9, change_message='edited Transaction')
    return render_view(request, 'admin/edit_transaction.html',
                       {'transaction': transaction, 'form': form})


def stuff_transaction_list(user, status=1):
    '''
    status
    (1)-successful,
    (2)-pending,
    (3)-Failed,
    (4)-All,
    (6)-successful bills
    (7)-All bills
    (8)-All non bill transactions
    (9)-All pending bills
    (10)-All failed bills
    (11)-All cancelled bills
    '''
    transaction_list = False
    if status == 1:
        transaction_list = Transaction.objects.filter(
            visa_success=True, is_processed=True, amount_sent__isnull=False, utility=False)
    elif status == 2:
        transaction_list = Transaction.objects.filter(
            visa_success=True, is_processed=False, amount_sent__isnull=False, utility=False)
    elif status == 3:
        transaction_list = Transaction.objects.filter(
            visa_success=False, utility=False)
    elif status == 4:
        #transaction_list = Transaction.objects.all()
        transaction_list = Transaction.objects.filter(utility=False)

    elif status == 5:
        transaction_list = Transaction.objects.filter(
            is_canceled=True, visa_success=True, is_processed=True, amount_sent__isnull=False, utility=False
        )

    elif status == 6:
        transaction_list = Transaction.objects.filter(
            visa_success=True, is_processed=True, amount_sent__isnull=False, utility=True
        )

    elif status == 7:
        transaction_list = Transaction.objects.filter(
            utility=True
        )

    elif status == 8:
        transaction_list = Transaction.objects.filter(
            utility=False
        )

    elif status == 9:
        transaction_list = Transaction.objects.filter(
            visa_success=True, is_processed=False, amount_sent__isnull=False, utility=True)

    elif status == 10:
        #
        transaction_list = Transaction.objects.filter(
            visa_success=False, utility=True)

    elif status == 11:
        transaction_list = Transaction.objects.filter(
            is_canceled=True, visa_success=True, is_processed=True, amount_sent__isnull=False, utility=True
        )

    # else:
    #     if len(transaction_list) > 0:
    #         transaction_list = transaction_list.filter(utility=False)

    '''get the transaction list our stuff users are allowed access to'''
    if transaction_list and not user.is_superuser:
        country_filter = network_filter = Q()
        for value, keyword in get_country_access(user):
            country_filter |= Q(to_country__code=value)
        for value, keyword in get_network_access(user):
            network_filter |= Q(mobile_network_code=value)
        #transaction_list = Transaction.objects.filter(country_filter & network_filter)
        transaction_list = transaction_list.filter(
            country_filter & network_filter)

    # if successful:
    #    transaction_list = transaction_list.filter(
    #        visa_success=True, is_processed=True, amount_sent__isnull=False)
    return transaction_list


@permission_required('view_transaction')
def transactions(request, name=False, user_id=False):
    '''
    Transactions
    '''
    pretitle = 'Pending Transactions'
    page_title = 'Pending Transactions'

    #debug(get_country_access(request.user), 'country')
    transaction_list = False
    status = 4
    if not name and request.user.is_superuser:
        page_title = pretitle = 'Transactions'
    elif name == 'pending':
        status = 2
        # transaction_list = transaction_list.filter(
        #    visa_success=True, is_processed=False, amount_sent__isnull=False)
    elif name == 'successful':
        status = 1
        page_title = pretitle = 'Successful Transactions'
        # transaction_list = transaction_list.filter(
        #    visa_success=True, is_processed=True, amount_sent__isnull=False)
    elif name == 'failed':
        status = 3
        page_title = pretitle = 'Failed Transactions'
    elif name == 'canceled':
        status = 5
        page_title = pretitle = 'Canceled Transactions'
        #transaction_list = transaction_list.filter(visa_success=False)
    elif name == 'search':
        page_title = pretitle = 'Search Transactions'

    elif name == 'billpayments':
        status = 6
        page_title = pretitle = 'Search Billpayments'
    else:
        return HttpResponseRedirect(reverse('admin:admin_dashboard'))

    # search query
    if 'q' in request.GET:
        try:
            id = int(request.GET['q']) ^ 0xABCDEFAB
            transaction_list = transaction_list.filter(id=id)
        except Exception, e:
            messages.error(request, "The Transaction was not found")
        if not transaction_list:
            try:
                num = str(request.GET['q'])
                ctry_code = num[:3]
                debug(ctry_code)
                phone_num = num[3:]
                debug(phone_num)
                transaction_list.filter(receiver_number=phone_num)
            except Exception, e:
                debug(e)

            # if request.user.is_superuser:
            #    transaction_list = Transaction.objects.all()
    transaction_list = stuff_transaction_list(request.user, status)

    # we are dealing with a specific user
    if user_id and transaction_list:
        user_id = int(user_id) ^ 0xABCDEFAB
        profile = get_object_or_404(Profile.objects.filter(id=user_id))
        transaction_list = transaction_list.filter(user=profile.user)

    if transaction_list:
        transaction_list = transaction_list.order_by('-id')

    paginator = Paginator(transaction_list, settings.PAGNATION_LIMIT)
    page = request.GET.get('page')
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        transactions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        transactions = paginator.page(paginator.num_pages)
    log_action(request, model_object=transaction_list,
               action_flag=6, change_message='view Transaction')
    return render_view(request, 'admin/transactions.html', {'transactions': transactions, 'pretitle': pretitle, 'page_title': page_title, 'type': name})



def tradelance(request):
    """work with tradelance."""
    pretitle = 'Pending Transactions'
    page_title = 'Pending Transactions'
    response_data = {}
    return render_view(request,'admin/tradelance.html',
    {'result':response_data
    })

def tradelance_response(request):
    """Tradelance response."""
    phone = None
    amount = None
    tlance_method = None
    response_data = {}
    pesapot = PesaPot()

    if request.POST:
        data = request.POST.copy()
        amount = data.get('tlance_amount','')
        number = data.get('tlance_number','')
        tlance_id = data.get('tlance_status','')
        tlance_method = data.get('selected_tmethod','')

        if tlance_method == 'tlance_deposit':
            response_data = pesapot.TradelanceDeposit(number,amount)
        elif tlance_method == 'tlance_request':
            response_data = pesapot.TradelanceRequest(number,amount)
        elif tlance_method == 'tlance_balance':
            response_data = pesapot.TradelanceBalance()

        elif tlance_method == 'tlance_status':
            response_data = pesapot.TradelanceStatus(tlance_id)




    return render_view(request,'admin/tradelance_response.html',
    {'result':response_data})




@permission_required('view_transaction')
def bill_transactions(request, name=False, user_id=False):
    '''
    Transactions
    '''
    pretitle = 'Pending Transactions'
    page_title = 'Pending Transactions'

    #debug(get_country_access(request.user), 'country')
    transaction_list = False
    status = 7
    if not name and request.user.is_superuser:
        page_title = pretitle = 'Bill Transactions'
    elif name == 'pending':
        status = 9
        # transaction_list = transaction_list.filter(
        #    visa_success=True, is_processed=False, amount_sent__isnull=False)
    elif name == 'successful':
        status = 6
        page_title = pretitle = 'Successful Bill Transactions'
        # transaction_list = transaction_list.filter(
        #    visa_success=True, is_processed=True, amount_sent__isnull=False)
    elif name == 'failed':
        status = 10
        page_title = pretitle = 'Failed Bill Transactions'
    elif name == 'canceled':
        status = 11
        page_title = pretitle = 'Canceled Bill Transactions'
        #transaction_list = transaction_list.filter(visa_success=False)
    elif name == 'search':
        page_title = pretitle = 'Search Transactions'
    else:
        return HttpResponseRedirect(reverse('admin:admin_dashboard'))

    # search query
    if 'q' in request.GET:
        try:
            id = int(request.GET['q']) ^ 0xABCDEFAB
            transaction_list = transaction_list.filter(id=id)
        except Exception, e:
            messages.error(request, "The Transaction was not found")
        if not transaction_list:
            try:
                num = str(request.GET['q'])
                ctry_code = num[:3]
                debug(ctry_code)
                phone_num = num[3:]
                debug(phone_num)
                transaction_list.filter(receiver_number=phone_num)
            except Exception, e:
                debug(e)

            # if request.user.is_superuser:
            #    transaction_list = Transaction.objects.all()
    transaction_list = stuff_transaction_list(request.user, status)

    # we are dealing with a specific user
    if user_id and transaction_list:
        user_id = int(user_id) ^ 0xABCDEFAB
        profile = get_object_or_404(Profile.objects.filter(id=user_id))
        transaction_list = transaction_list.filter(user=profile.user)

    if transaction_list:
        transaction_list = transaction_list.order_by('-id')

    paginator = Paginator(transaction_list, settings.PAGNATION_LIMIT)
    page = request.GET.get('page')
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        transactions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        transactions = paginator.page(paginator.num_pages)
    log_action(request, model_object=transaction_list,
               action_flag=6, change_message='view Transaction')
    return render_view(request, 'admin/bill_transactions.html', {'transactions': transactions, 'pretitle': pretitle, 'page_title': page_title, 'type': name})


@permission_required('edit_transaction')
def resend_transaction(request):
    '''
    Resend the user transaction
    '''
    if request.POST:
        if not 'resend_transaction' in request.POST:
            return HttpResponseRedirect(reverse('admin:admin_dashboard'))
        else:
            name = int(request.POST['resend_transaction'])
            id = name ^ 0xABCDEFAB
            transaction = get_object_or_404(Transaction.objects.filter(
                id=id, visa_success=True, is_processed=False, amount_sent__isnull=False), id=id, visa_success=True, is_processed=False, amount_sent__isnull=False)
            response = {}
            response = payments.process_mobilemoney(
                transaction, response, request, processed_by=request.user)
            #debug(response, 'Resend Response')
            # if not response['error'] and  'delivered_to_mobile' in response :
            # reget the transaction
            transaction = get_object_or_404(Transaction.objects.filter(id=id))
            if transaction.is_processed:
                success_message(request, 'admin_resend_transaction', {
                                'response': response})
            # else:
            #        error_message(request, 'admin_resend_transaction', {'response': response})
            else:
                error_message(request, 'admin_process_transaction', {
                              'response': response})
    else:
        return HttpResponseRedirect(reverse('custom_404'))
    return HttpResponseRedirect(reverse('admin:admin_transaction', args=(name,)))


@permission_required('edit_transaction')
def process_transaction(request):
    '''
    Mark as processed with resending
    '''

    if request.POST:
        cancel_transaction = request.POST.get('cancel_transaction', None)
        process_transaction = request.POST.get('process_transaction', None)
        if cancel_transaction:
            name = cancel_transaction
            id = int(name) ^ 0xABCDEFAB
            transaction = get_object_or_404(Transaction.objects.filter(
                id=id, visa_success=True, is_processed=False, amount_sent__isnull=False), id=id, visa_success=True, is_processed=False, amount_sent__isnull=False)
        elif process_transaction:
            name = process_transaction
            id = int(name) ^ 0xABCDEFAB
            transaction = get_object_or_404(Transaction.objects.filter(
                id=id, visa_success=True, is_processed=False, amount_sent__isnull=False), id=id, visa_success=True, is_processed=False, amount_sent__isnull=False)
        else:
            return HttpResponseRedirect(reverse('custom_404'))

        if process_transaction:
            response = {'status_code': payments.RESPONSE_CODES['SUCCESS']}
            payments.process_mobilemoney(
                transaction, response, request, processed_by=request.user, mark_as_processed=True)
            _process_error = response.get('error', None)
            if not _process_error:
                delivered_to_mobile = False
                if 'delivered_to_mobile' in response:
                    delivered_to_mobile = response['delivered_to_mobile']
                success_message(request, 'admin_process_transaction', {
                                'status_code': response['status_code'], 'delivered_to_mobile': delivered_to_mobile})
                return HttpResponseRedirect(reverse('admin:admin_transaction', args=(name,)))
            else:
                error_message(request, 'admin_process_transaction', {
                              'status_code': response['status_code']})
        if cancel_transaction:
            transaction.is_processed = True
            transaction.is_canceled = True
            transaction.canceled_by = request.user
            transaction.cancled_on = datetime.now()
            transaction.save()
            return HttpResponseRedirect(reverse('admin:admin_transactions', args=('canceled',)))
    # return HttpResponseRedirect(settings.BASE_URL +
    # 'admin/transactions/successful/')
    return HttpResponseRedirect(reverse('admin:admin_transactions', args=('pending',)))


@admin_required
def users(request, name):
    '''
    @request  request object
    '''
    # user_list = Profile.objects.filter(account_verified=True,user__isnull=False)
    # print name
    pretitle = 'verified users'
    page_title = 'verified users'
    if name == 'verified':
        user_list = admin_utils.verified_users()
    elif name == 'unverified':
        user_list = Profile.objects.filter(
            Q(id_pic=''),
            account_verified=False,
            user__isnull=False, account_blocked=False)
        pretitle = 'Unverified Users'
        page_title = 'verified users'
    elif name == 'pending_verification':
        pretitle = 'Users waiting to be verified'
        page_title = 'users pending verification'
        user_list = admin_utils.users_pending_verification()
    elif name == 'blocked':
        pretitle = 'Blocked Users'
        page_title = 'Blocked Users'
        user_list = admin_utils.blocked_users()
    elif name == 'top':
        pretitle = 'Blocked Users'
        page_title = 'Blocked Users'
        user_list = Profile.objects.filter(account_blocked=False)
    elif name == 'search':
        pretitle = 'User Search'
        page_title = 'User Search'
        user_list = Profile.objects.filter(user__isnull=False)
    else:
        return HttpResponseRedirect(reverse('custom_404'))

    user_list = user_list.filter().order_by('-id')
    # search query
    if 'q' in request.GET:
        pretitle += ' | %s' % request.GET['q']
        page_title += ' | %s' % request.GET['q']
        user_list = user_list.filter(
            Q(firstname__icontains='' + request.GET['q'] + '') | Q(lastname__icontains='' + request.GET['q'] + ''))

    paginator = Paginator(user_list, settings.PAGNATION_LIMIT)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users = paginator.page(paginator.num_pages)
    log_action(request, model_object=user_list,
               action_flag=13, change_message='searched user')
    return render_view(request, 'admin/users.html', {'users': users, 'pretitle': pretitle, 'page_title': page_title})


@superuser_required
def stuff_users(request, name=False):
    '''fetch stuff '''
    user_list = AdminProfile.objects.all()  # (is_staff=True)
    debug(user_list, 'stuff')
    user_list = user_list.filter().order_by('-id')
    # search query
    if 'q' in request.GET:
        pretitle += ' | %s' % request.GET['q']
        page_title += ' | %s' % request.GET['q']
        user_list = user_list.filter(
            Q(username__icontains='' + request.GET['q'] + ''))
    paginator = Paginator(user_list, settings.PAGNATION_LIMIT)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users = paginator.page(paginator.num_pages)
    return render_view(request, 'admin/stuff_users.html', {'users': users})



@superuser_required
def health_users(request, name=False):
    '''fetch stuff '''
    user_list = AdminProfile.objects.all()  # (is_staff=True)
    debug(user_list, 'stuff')
    user_list = user_list.filter().order_by('-id')
    # search query
    if 'q' in request.GET:
        pretitle += ' | %s' % request.GET['q']
        page_title += ' | %s' % request.GET['q']
        user_list = user_list.filter(
            Q(username__icontains='' + request.GET['q'] + ''))
    paginator = Paginator(user_list, settings.PAGNATION_LIMIT)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users = paginator.page(paginator.num_pages)
    return render_view(request, 'admin/health_users.html', {'users': users})



@admin_required
def user(request, name):
    pretitle = 'User'
    page_title = 'User'
    id = int(name) ^ 0xABCDEFAB
    profile = get_object_or_404(Profile.objects.filter(id=id))
    pretitle = page_title = profile.get_names()
    userdata = {}

    if not check_user_permission(request.user, 'edit_profile'):
        # print "NOOOOO"
        return render_view(request, 'admin/user_readonly.html', {'name': name,
                                                                 'user_profile': profile,
                                                                 'pretitle': pretitle,
                                                                 'page_title': page_title,
                                                                 'userdata': userdata})
    else:
        if request.POST:
            if 'update_account' in request.POST:
                post_values = request.POST.copy()
                post_values['dob'] = datetime.strptime(
                    post_values['dob_month'] + '-' + post_values['dob_day'] + '-' + post_values['dob_year'], '%m-%d-%Y')
                form = ProfileUpdateForm(post_values, instance=profile)
                # debug(request.FILES)
                if 'passport' in request.FILES:
                    form.id_pic = request.FILES['passport']

                if form.is_valid():
                    if 'passport' in request.FILES:
                        profile.id_pic = request.FILES['passport']
                        profile.save()
                    #profile = Profile.objects.filter(id=profile.pk)
                    form.save()
                    success_message(request, 'admin_update_profile', {})
                else:
                    error_message(request, 'admin_update_profile', {})

        transaction_stats = Transaction.objects.filter(
            user=profile.user, visa_success=True, is_processed=True,
            amount_sent__isnull=False)
        userdata['successful_transactions'] = transaction_stats.count()
        if userdata['successful_transactions'] > 0:
            userdata['amount_sent'] = transaction_stats.aggregate(
                Sum('amount_sent'))
            if 'amount_sent__sum' in userdata['amount_sent']:
                userdata['amount_sent'] = userdata[
                    'amount_sent']['amount_sent__sum']
            top_amount_sent = transaction_stats.aggregate(Max('amount_sent'))
            if 'amount_sent__max' in top_amount_sent:
                userdata['top_amount_sent'] = top_amount_sent[
                    'amount_sent__max']
        return render_view(request, 'admin/user.html', {'name': name,
                                                        'user_profile': profile,
                                                        'pretitle': pretitle,
                                                        'page_title': page_title,
                                                        'userdata': userdata})


@superuser_required
def charges_limits(request, code):
    active_country = get_object_or_404(Country.objects.filter(code=code))
    rate = Charge.objects.get(country=active_country)
    countries = Country.objects.all()
    form = ChargesLimitsForm()
    if request.POST:
        form = ChargesLimitsForm(request.POST, instance=rate)
        if form.is_valid():
            form.save()
            messages.success(
                request, "The Charges & Limits Was Successfully Edited")
        else:
            print form.errors
    return render_view(request, 'admin/charges_limits.html',
                       {'rate': rate, 'pretitle': 'charges & limits',
                        'page_title': "charges & Limits",
                        'countries': countries,
                        'country_code': code,
                        'form': form}
                       )


#@admin_required
@permission_required('view_rate')
def rates(request, code):
    '''edit and check our rates'''
    active_country = get_object_or_404(Country.objects.filter(code=code))
    # Charge.objects.all().delete()
    rate = Charge.objects.get(country=active_country)
    countries = Country.objects.all()
    form = RateUpdateForm()
    if request.POST:
        form = RateUpdateForm(request.POST, instance=rate)
        if form.is_valid():
            form.save()
            messages.success(request, "The Rates Were Successfully Edited")
        else:
            print form.errors
    return render_view(request, 'admin/rates.html',
                       {'rate': rate, 'form': form, 'countries': countries}
                       )


@admin_required
def logs(request):
    return render_view(request, 'admin/logs.html', {})


def save_transaction(cur, user, pending=False):
    for row in cur.fetchall():
        debug(row, 'row data')
        cur.execute(
            "SELECT invoice_id,phon_num,phon_ext,amount_received,amount,added,exchange_rate from transaction_log where log_id = %d " %
            row[0])
        datarow = cur.fetchone()
        if datarow:
            data = {
                'user': user.pk,
                'receiver_number': datarow[1],
                'receiver_country_code': datarow[2],
                'amount_sent': datarow[4],
                'processed_by': 1,
                'rate': datarow[6],
                'visa_success': True,
            }

            processed_on = datetime.fromtimestamp(int(datarow[5]))
            if not pending:
                data['processed_on'] = processed_on
                data['is_processed'] = True
            else:
                debug(data, 'Pending Transaction')
                data['is_processed'] = False
            data['amount_received'] = float(datarow[4]) * float(datarow[6])
            data['started_on'] = processed_on
            transaction = TransactionAddForm(data)
            if transaction.is_valid():
                try:
                    transaction.save()
                except IntegrityError as e:
                    print e
            else:
                print transaction.errors


@permission_required('view_audit_trail')
def audits_trails(request):
    '''system user actions'''
    from django.contrib.admin.models import LogEntry
    audit_logs_list = UserActions.objects.all()

    # unique actions
    unique_actions = []
    # if settings.IS_SQLITE:
    log_entrys = LogEntry.objects.all()
    for log_entry in log_entrys:
        if log_entry.action_flag not in unique_actions:
            unique_actions.append(log_entry.action_flag)

    # unique users
    unique_users = []
    # if settings.IS_SQLITE:
    for log_entry in audit_logs_list:
        if log_entry.user not in unique_users:
            unique_users.append(log_entry.user)
    # else:
    #    unique_users = audit_logs_list.distinct(
    #        'user')

    # debug(unique_actions,'unique_actions')

    if 'start_date' in request.GET:
        start_date = '%s' % request.GET['start_date']
        start_date = datetime.strptime(start_date, '%d-%m-%Y')
    else:
        first_log_entry = LogEntry.objects.values_list(
            'action_time', flat=True).order_by('id')[:1]
        start_date = first_log_entry[0]

    if 'end_date' in request.GET:
        end_date = '%s' % request.GET['end_date']
        end_date = datetime.strptime(end_date, '%d-%m-%Y')
    else:
        end_date = datetime.now()

    try:
        end_date = pytz.utc.localize(end_date)
        start_date = pytz.utc.localize(start_date)
    except Exception, e:
        pass

    if start_date == end_date:
        audit_logs_list = audit_logs_list.filter(
            log_entry__action_time__contains=start_date.date())
    else:
        audit_logs_list = audit_logs_list.filter(
            log_entry__action_time__range=(start_date, end_date))

    action_type = request.GET.get('action_type', None)
    if action_type and not action_type == 'All':
        audit_logs_list.filter(log_entry__action_flag=action_type)

    start_date = '%s-%s-%s' % (
        start_date.day, start_date.month, start_date.year)
    end_date = '%s-%s-%s' % (end_date.day, end_date.month, end_date.year)

    audit_logs_list = audit_logs_list.order_by('-id')

    paginator = Paginator(audit_logs_list, settings.PAGNATION_LIMIT)
    page = request.GET.get('page')
    try:
        audit_logs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        audit_logs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        audit_logs = paginator.page(paginator.num_pages)
    # debug(audit_logs_list,'Logs')
    return render_view(request, 'audits.html',
                       {'audit_logs': audit_logs,
                        'unique_actions': unique_actions,
                        'start_date': start_date,
                        'end_date': end_date,
                        'unique_users': unique_users,
                        }
                       )


@permission_required('view_reports')
def reports(request):
    # we only pick successful transactions
    profile = AdminProfile.objects.get(user=request.user)

    # = COUNTRY_CHOICES[profile.country]
    if 'end_date' in request.GET:
        end_date = '%s' % request.GET['end_date']
        end_date = datetime.strptime(end_date, '%d-%m-%Y')
    else:
        end_date = datetime.now()

    if 'start_date' in request.GET:
        start_date = '%s' % request.GET['start_date']
        start_date = datetime.strptime(start_date, '%d-%m-%Y')
    else:
        #start_date = end_date - relativedelta(years=1)
        first_successful_transaction = Transaction.objects.filter(
            visa_success=True,
            is_processed=True,
            amount_sent__isnull=False
        ).values_list(
            'processed_on', flat=True).order_by('id')[:1]
        # start_date = "%d-%m-%Y".format(rstart_date[0])
        # #datetime.strptime(rstart_date[0], '%d-%m-%Y')
        if len(first_successful_transaction) > 0:
            start_date = first_successful_transaction[0]
        else:
            start_date = end_date
    # make dates datezone aware
    try:
        end_date = pytz.utc.localize(end_date)
        start_date = pytz.utc.localize(start_date)
    except Exception, e:
        debug(e, 'localize time error', 'admin')
        pass

    status = request.GET.get('status', 1)
    # if request.GET['status']:
    transaction_list = stuff_transaction_list(request.user, int(status))

    countries_list = transaction_list.values_list(
        'sender_country', flat=True).distinct()

    if start_date == end_date:
        transaction_list = transaction_list.filter(
            Q(started_on__startswith=start_date.date()) | Q(
                started_on__startswith=end_date.date()),
        )
        # print transaction_list
    else:
        transaction_list = transaction_list.filter(
            Q(started_on__range=(start_date, end_date)) | Q(
                started_on__startswith=start_date.date()) | Q(started_on__startswith=end_date.date())
        )

    number_of_trasactions = amount_transfered = number_of_unique_senders = average_transaction_amount = 0
    if transaction_list:

        transaction_list = transaction_list.order_by('processed_on')

        # get filters need to come before sums
        # filter the network
        if 'network' in request.GET and not request.GET['network'] == 'All':
            transaction_list = transaction_list.filter(
                mobile_network_code=request.GET['network'])
        if 'ctry' in request.GET and not request.GET['ctry'] == 'All':

            transaction_list = transaction_list.filter(
                to_country__code=request.GET['ctry'])

        if 'sender_ctry' in request.GET and not request.GET['sender_ctry'] == 'All':
            transaction_list = transaction_list.filter(
                sender_country=request.GET['sender_ctry'])

        # if 'sender_ctry':
        #    transaction_list = transaction_list.filter(album__artist__id=123)
        if transaction_list:
            number_of_trasactions = transaction_list.count()
            amount_transfered = transaction_list.aggregate(
                Sum('amount_received'))
            if 'amount_received__sum' in amount_transfered:
                amount_transfered = amount_transfered['amount_received__sum']

            if settings.IS_SQLITE:
                number_of_unique_senders = []
                for t_user in transaction_list:
                    if t_user.user not in number_of_unique_senders:
                        number_of_unique_senders.append(t_user.user)
                number_of_unique_senders = len(number_of_unique_senders)
            else:
                # number_of_unique_senders = transaction_list.distinct(
                #    'user').count()
                number_of_unique_senders = transaction_list.values_list(
                    'user', flat=True).distinct()

            # if len(l) > 0 else float('nan')
            average_transaction_amount = amount_transfered / \
                number_of_trasactions

    start_date = '%s-%s-%s' % (
        start_date.day, start_date.month, start_date.year)
    end_date = '%s-%s-%s' % (end_date.day, end_date.month, end_date.year)

    # restrict a user to thier
    countries = get_country_access(request.user)
    networks = get_network_access(request.user)

    if request.POST:
        if 'generate_report' in request.POST:
            return generate_csv_report(transaction_list, request.user)

    paginator = Paginator(transaction_list, settings.PAGNATION_LIMIT)
    page = request.GET.get('page')
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        transactions = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        transactions = paginator.page(paginator.num_pages)

    return render_view(request, 'reports.html', {'transactions': transactions,
                                                 'start_date': start_date,
                                                 'end_date': end_date,
                                                 'number_of_trasactions': number_of_trasactions,
                                                 'amount_transfered': amount_transfered,
                                                 'number_of_unique_senders': number_of_unique_senders,
                                                 'average_transaction_amount': average_transaction_amount,
                                                 'countries': countries,
                                                 'networks': networks,
                                                 'countries_list': countries_list,
                                                 })


@superuser_required
def edit_stuff_user(request, name):
    id = int(name) ^ 0xABCDEFAB
    user = get_object_or_404(AdminProfile.objects.filter(id=id))
    form = EditAdminUserForm()
    if request.POST:
        form = EditAdminUserForm(request.POST, instance=user.user)
        if form.is_valid():

            # update user password
            if form.cleaned_data['password']:
                #user.user.password = form.cleaned_data['password']
                user.user.set_password(form.cleaned_data['password'])

            # update user permissions
            assign_permissions(user.user, form, update=True)
            user.user.save()

            messages.success(request, "The Stuff User Was Successfully Edited")
    country_access = get_country_access(user.user)
    network_access = get_network_access(user.user)
    edit_permissions = get_user_permissions(user.user)

    return render_view(request, 'admin/edit_stuff_user.html',
                       {'stuff_profile': user,  'NETWORK_CHOICES': NETWORK_CHOICES,
                        'COUNTRY_CHOICES': COUNTRY_CHOICES, 'form': form,
                        'country_access': country_access, 'network_access': network_access,
                        'edit_permissions': edit_permissions}
                       )


@superuser_required
def create_customer_care_user(request):
    '''create a customer care user'''
    return create_stuff_user(request, is_customer_care=True)


@superuser_required
def create_stuff_user(request, is_customer_care=False):
    '''create an admin user'''
    form = CreateAdminUserForm()
    if request.POST:
        form = CreateAdminUserForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password'])
            user.save()
            user.is_staff = True
            # user.save()
            # assign user permissions
            update = False
          
            user.save()

            # save profile options
            profile = AdminProfile(user=user,category=form.cleaned_data['category'],cat_name=form.cleaned_data['cat_name'],doct_name=form.cleaned_data['doct_name'],phone=form.cleaned_data['phone'],region=form.cleaned_data['region'],districts=form.cleaned_data['districts'],info=form.cleaned_data['info'])
            profile.is_customer_care = is_customer_care
            # if form.cleaned_data['reports'] == '2':
            #    profile.is_customer_care = True
            if form.cleaned_data['role'] == 'lawyer':
                profile.is_lawyer = True
            if form.cleaned_data['role'] == 'doctor':
                profile.is_doctor = True
            if form.cleaned_data['role'] == 'jounalist':
                profile.is_jounalist = True
            if form.cleaned_data['role'] == 'education':
                profile.is_educ = True
          
            profile.save()
            # user = form.save()
            # user.is_staff = True
            # user.save()
            # debug(user)
            messages.success(request, "The User Was Successfully Created")
    return render_view(request, 'create_stuff_user.html', {'form': form, 'NETWORK_CHOICES': NETWORK_CHOICES, 'COUNTRY_CHOICES': COUNTRY_CHOICES, 'is_customer_care': is_customer_care}
                       )

def add_health_info(request, is_customer_care=False):

    '''create an admin user'''
    form = AddHealthInfoForm()
    title_health = request.POST.get('title_health','')
    message = request.POST.get('message','')

    print 'Subject ', title_health
    print 'Message ', message
    
    form = AddHealthInfoForm(request.POST)
    if request.POST:
        if form.is_valid():
            health_info = HealthInfo(msg=message, sub=title_health)
            health_info.save()
           

            print 'Success'
            # user.save()
            # assign user permissions
            update = False
          
            
          
            messages.success(request, "The Info Was Successfully Created")
    return render_view(request, 'add_health_info.html', {'form': form})



def add_law_info(request, is_customer_care=False):

    '''create an admin user'''
    form = AddLawInfoForm()
    sub = request.POST.get('sub','')
    msg = request.POST.get('msg','')

    print 'Subject ', sub
    print 'Message ', msg
    
    form = AddLawInfoForm(request.POST)
    if request.POST:
        if form.is_valid():
            law_info = LawhInfo(msg=msg, sub=sub)
            law_info.save()
           

            print 'Success'
            # user.save()
            # assign user permissions
            update = False
          
            
          
            messages.success(request, "The Info Was Successfully Created")
    return render_view(request, 'add_law_info.html', {'form': form})



def add_pub_info(request, is_customer_care=False):

    '''create an admin user'''
    form = AddPubInfoForm()
    sub = request.POST.get('sub','')
    msg = request.POST.get('msg','')

    print 'Subject ', sub
    print 'Message ', msg
    
    form = AddPubInfoForm(request.POST)
    if request.POST:
        if form.is_valid():
            pub_info = JounalisthInfo(msg=msg, sub=sub)
            pub_info.save()
           

            print 'Success'
            # user.save()
            # assign user permissions
            update = False
          
            
          
            messages.success(request, "The Info Was Successfully Created")
    return render_view(request, 'add_law_info.html', {'form': form})


def add_educ_info(request, is_customer_care=False):

    '''create an admin user'''
    form = AddEducInfoForm()
    sub = request.POST.get('sub','')
    msg = request.POST.get('msg','')

    print 'Subject ', sub
    print 'Message ', msg
    
    form = AddEducInfoForm(request.POST)
    if request.POST:
        if form.is_valid():
            educ_info = EducationInfo(msg=msg, sub=sub)
            educ_info.save()
           

            print 'Success'
            # user.save()
            # assign user permissions
            update = False
          
            
          
            messages.success(request, "The Info Was Successfully Created")
    return render_view(request, 'add_educ_info.html', {'form': form})



@superuser_required
def create_educ_user(request, is_customer_care=False):
    '''create an admin user'''
    form = CreateEducUserForm()
    if request.POST:
        form = CreateEducUserForm(request.POST)
        if form.is_valid():
            user = Create_Health_User(
                username=form.cleaned_data['username'],email=form.cleaned_data['email'],category=form.cleaned_data['category'],cat_name=form.cleaned_data['cat_name'],doct_name=form.cleaned_data['doct_name'],speciality=form.cleaned_data['speciality'],password=form.cleaned_data['password'],phone=form.cleaned_data['phone'],region=form.cleaned_data['region'],districts=form.cleaned_data['districts'], info=form.cleaned_data['info'])

            user.save()
            
            # user.save()
            # assign user permissions
            update = False
        
            messages.success(request, "The User Was Successfully Created")
    return render_view(request, 'create_health_user.html', {'form': form}
                       )




def assign_permissions(user, form, update=False, is_customer_care=False):
    '''assign staff members permissions'''
    if user:

        if is_customer_care:
            # customer care options
            content_type = ContentType.objects.get_for_model(Transaction)
            view_transaction = Permission.objects.get(
                content_type=content_type, codename="view_transaction")
            edit_transactions = Permission.objects.get(
                content_type=content_type, codename="edit_transaction")
            user.user_permissions.add(view_transaction)
            user.user_permissions.remove(edit_transactions)

        else:
            content_type = ContentType.objects.get_for_model(Profile)
            view_profile = Permission.objects.get(
                content_type=content_type, codename="view_profile")
            edit_profile = Permission.objects.get(
                content_type=content_type, codename="edit_profile")
            if form.cleaned_data['users'] == '2':
                user.user_permissions.add(view_profile)
                user.user_permissions.remove(edit_profile)
            elif form.cleaned_data['users'] == '3':
                user.user_permissions.add(edit_profile, view_profile)
            if update and form.cleaned_data['users'] == '1':
                user.user_permissions.remove(edit_profile, view_profile)

            # rates edit permissions
            content_type = ContentType.objects.get_for_model(Rate)
            view_rate = Permission.objects.get(
                content_type=content_type, codename="view_rate")
            edit_rate = Permission.objects.get(
                content_type=content_type, codename="edit_rate")
            if form.cleaned_data['rates'] == '2':
                user.user_permissions.add(view_rate)
                user.user_permissions.remove(edit_rate)
            elif form.cleaned_data['rates'] == '3':
                user.user_permissions.add(view_rate, edit_rate)
            if update and form.cleaned_data['rates'] == '1':
                user.user_permissions.remove(edit_rate, view_rate)

            # transaction edit permissions
            content_type = ContentType.objects.get_for_model(Transaction)
            view_transaction = Permission.objects.get(
                content_type=content_type, codename="view_transaction")
            edit_transactions = Permission.objects.get(
                content_type=content_type, codename="edit_transaction")
            if form.cleaned_data['transactions'] == '2':
                user.user_permissions.add(view_transaction)
                user.user_permissions.remove(edit_transactions)
            elif form.cleaned_data['transactions'] == '3':
                user.user_permissions.add(view_transaction, edit_transactions)
            if update and form.cleaned_data['transactions'] == '1':
                user.user_permissions.remove(
                    edit_transactions, view_transaction)

            # reports
            content_type = ContentType.objects.get_for_model(Transaction)
            view_reports = Permission.objects.get(
                content_type=content_type,
                codename="view_reports"
            )
            if form.cleaned_data['reports'] == '2':
                user.user_permissions.add(view_reports)
            if update and form.cleaned_data['reports'] == '1':
                user.user_permissions.remove(view_reports)

            # audit trails
            content_type = ContentType.objects.get_for_model(AdminProfile)
            view_audit_trail = Permission.objects.get(
                content_type=content_type, codename="view_audit_trail")
            try:
                if form.cleaned_data['audit_trail'] == '2':
                    user.user_permissions.add(view_audit_trail)
                if update and form.cleaned_data['audit_trail'] == '1':
                    user.user_permissions.remove(view_audit_trail)
            except Exception, e:
                print e
            user.save()


def download_image(name, image, url):
    input_file = StringIO(urllib2.urlopen(url).read())
    output_file = StringIO()
    img = Image.open(input_file)
    if img.mode != "RGB":
        img = img.convert("RGB")
    img.save(output_file, "JPEG")
    image.save(name, ContentFile(output_file.getvalue()), save=False)


@permission_required('edit_user')
def contact_user(request, name):
    id = int(name) ^ 0xABCDEFAB
    profile = get_object_or_404(Profile.objects.filter(id=id))
    reasons = EmailSupport.EMAIL_REASON
    form = ContactUserForm()
    if request.POST:
        data = request.POST.copy()
        data['user'] = profile.user.pk
        #user = User.objects.get(user=request.user)
        data['support_staff'] = request.user.id
        if not 'subject' in data:
            reason = request.POST['reason']
            reason = [(age, person_id)
                      for (age, person_id) in reasons if age == reason]
            data['subject'] = reason[0][1]
        #debug(data,'Contact Form Database')
        form = ContactUserForm(data)
        if form.is_valid():
            form.save()
            template = settings.EMAIL_TEMPLATE_DIR + 'support.html'
            try:
                staff = Profile.objects.get(user=request.user)
                data['support_staff_names'] = staff.get_names()
            except Exception, e:
                pass

            data['user_names'] = profile.get_names()
            mailer(request, data['subject'],
                   template, data, profile.user.email)
            messages.success(request, 'The Message Was Successfully sent')
    support_emails = EmailSupport.objects.filter(
        user=profile.user).order_by('-id')
    return render_view(request, 'contact_user.html', {'user_profile': profile, 'form': form, 'reasons': reasons, 'support_emails': support_emails})


@superuser_required
def delete_user(request):
    '''delete user'''
    if not request.POST or not 'delete_user' in request.POST:
        log_unauthorized_access(request)
        return HttpResponseRedirect(reverse('custom_404'))

    transactions = Transactions.objects.get(user=request.user)
    transactions.delete()

    phonebook = Phonebook.objects.get(user=request.user)
    phonebook.delete()

    user = User.objects.get(user=request.user)
    user.delete()

    return HttpResponseRedirect(reverse('custom_404'))


def admin_503(request):
    return render_view(request, 'admin_503.html', {})


def generate_csv_report(transaction, user=False, _file=False):
    '''generate a csv report'''
    import csv
    from django.utils.encoding import smart_str

    date = datetime.today().strftime("%B-%d-%Y")
    response = HttpResponse(content_type='text/csv')

    if _file:
        '''if we want a'''
        response = StringIO()
    else:
        response[
            'Content-Disposition'] = 'attachment; filename="report_%s.csv"' % date
    writer = csv.writer(response)

    header = [
        smart_str(u"Transaction ID"),
        smart_str(u"MOM Transaction ID"),
        smart_str(u"Date"),
        smart_str(u"Sender names"),
        smart_str(u"Sender number"),
        smart_str(u"Sender country"),
        smart_str(u"Currency"),
        smart_str(u"Recipient name"),
        smart_str(u"Recipient number"),
        smart_str(u"Amount"),
        smart_str(u"Status"),
        smart_str(u"Revenue Share"),
    ]

    if user:
        if user.is_superuser:
            header.append(smart_str(u"Mobile network"))
            header.append(smart_str(u"USD Amount Sent"))
            #header.append(smart_str(u"Exchange Rate"))

    writer.writerow(header)
    for t in transaction:
        if t.actual_delivery_date:
            t_date = t.actual_delivery_date
        else:
            t_date = t.actual_initiation_date
        content = [
            smart_str(t.get_invoice()),
            smart_str(t.get_network_transactionid()),
            smart_str(t_date),
            smart_str(t.get_sender_profile().get_names()),
            smart_str(t.get_sender_profile().get_phonenumber()),
            smart_str(t.sender_country),
            smart_str(t.currency_sent),
            smart_str(t.recipient_names()),
            smart_str(t.recipient_number()),
            smart_str(t.amount_received),
            smart_str(t.actual_status),
            smart_str(t.revenue_share()),
        ]

        if user:
            if user.is_superuser:
                content.append(smart_str(t.get_mobile_network()))
                content.append(smart_str(t.amount_sent))
                # content.append(smart_str(t.exchange_rate))

        writer.writerow(content)
    return response


@permission_required('view_transaction')
def phonenumber_transaction_search(request):
    '''phonenumber transaction search'''
    form = transactionPhonenumberSearchForm()
    transaction_list = []
    transactions = {}
    if request.GET:
        form = transactionPhonenumberSearchForm(request.GET)
        if form.is_valid():
            phon_num = '%s' % request.GET.get('phonenumber', '')
            try:
                '''search by Transaction id'''
                invoice_id = int(phon_num) ^ 0xABCDEFAB
                transaction_list = Transaction.objects.filter(pk=invoice_id)
            except Exception, e:
                print e
                pass

            if len(transaction_list) < 1:
                '''search by operator id'''
                transaction_list = Transaction.objects.filter(
                    mobile_response_code=phon_num
                )

            if len(transaction_list) < 1:
                '''search by Transaction phonenumber'''
                transaction_list = Transaction.objects.filter(
                    receiver_number=phon_num
                )

            user = request.user
            if len(transaction_list) > 0:
                country_filter = network_filter = Q()
                for value, keyword in get_country_access(user):
                    print "Country access Value: %s , keyword: %s" % (value, keyword)
                    country_filter |= Q(to_country__code=value)
                for value, keyword in get_network_access(user):
                    network_filter |= Q(mobile_network_code=value)
                #transaction_list = Transaction.objects.filter(country_filter & network_filter)
                transaction_list = transaction_list.filter(
                    country_filter & network_filter)

                paginator = Paginator(
                    transaction_list, settings.PAGNATION_LIMIT)
                page = request.GET.get('page')
                try:
                    transactions = paginator.page(page)
                except PageNotAnInteger:
                    # If page is not an integer, deliver first page.
                    transactions = paginator.page(1)
                except EmptyPage:
                    # If page is out of range (e.g. 9999), deliver last page of
                    # results.
                    transactions = paginator.page(paginator.num_pages)

    return render_view(request, 'phonenumber_transaction_search.html',
                       {'form': form, 'transactions': transactions})


@superuser_required
def export_data(request):
    '''generate a csv report'''

    if request.POST:
        import csv
        from django.utils.encoding import smart_str

        date = datetime.today().strftime("%B-%d-%Y")
        response = HttpResponse(content_type='text/csv')

        filename = 'user_data'
        user_type = request.POST.get('data_type', None)
        user_list = {}
        if user_type == '1':
            user_list = admin_utils.verified_users()
            filename = 'verified_user_data'
        elif user_type == '2':
            user_list = admin_utils.users_pending_verification()
            filename = 'verification_pending_user_data'
        elif user_type == '3':
            user_list = admin_utils.blocked_users()
            filename = 'blocked_user_data'
        elif user_type == '4':
            user_list = admin_utils.unverified_users()
            filename = 'unverified_user_data'

        response[
            'Content-Disposition'] = 'attachment; filename="export_%s_%s.csv"' % (filename, date)
        import csv
        from django.utils.encoding import smart_str

        #csvfile = StringIO.StringIO()
        writer = csv.writer(response)

        header = [
            smart_str(u"Email"),
            smart_str(u"Phone number"),
            smart_str(u"Firstname"),
            smart_str(u"Lastname"),
            smart_str(u"Country"),
        ]
        writer.writerow(header)
        for t in user_list:
            content = [
                smart_str(t.user.email),
                smart_str(t.get_phonenumber()),
                smart_str(t.firstname),
                smart_str(t.lastname),
                smart_str(t.country),
            ]
            writer.writerow(content)
        return response
    return render_view(request, 'export_data.html', {})
