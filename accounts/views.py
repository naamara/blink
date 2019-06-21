# Create your views here.
from django.template import RequestContext
from django.shortcuts import HttpResponseRedirect, \
    get_object_or_404, HttpResponse, render_to_response
from accounts.forms import SignupForm,SignupForm2, AuthenticationForm, UserDetailsForm, AccessRestrictedForm, VerifyPhoneForm, PassportUploadForm, PassportUploadForm_jumio, RecoverPasswordForm, SetPasswordForm, landingSendForm, PasswordChangeForm, UpdatePhonenumberForm, UpdateEmailForm, UpdateAvatarForm
from accounts.models import Profile
from remit.views import home_page
from django.contrib import messages
import remit.settings as settings
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from remit.decorators import logged_out_required, ajax_required
from remit.utils import mailer, sendsms, error_message, success_message, debug
from datetime import datetime
from django.template.loader import render_to_string
import random
from remit.utils import urlsafe_base64_encode, urlsafe_base64_decode, admin_mail, get_user_location
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.utils.encoding import force_bytes
from accounts.utils import generate_email_confirmation_key
from django.core.urlresolvers import reverse
from remit_admin.utils import store_login_info
from ipware.ip import get_ip, get_real_ip


def render_view(request, template, data):
    '''
    wrapper for rendering views , loads RequestContext
    @request  request object
    @template  string
    @data  tumple
    '''
    if not request.user.is_authenticated():
        template = "v2/%s" % template
        data['STATIC_URL'] = '%sv2/' % settings.STATIC_URL
    return render_to_response(
        template, data,
        context_instance=RequestContext(request)
    )


@logged_out_required
def signup(request):
    '''
    handles the signup page
    @request  request object
    '''
    form = SignupForm()
    if request.user.is_authenticated():
        return home_page(request)
    if request.method == "POST":
        post_values = request.POST.copy()

        form = SignupForm(post_values)
        if form.is_valid():
            user = form.save()
            email, password, country_code, phonenumber = (
                form.cleaned_data['email'],
                form.cleaned_data['password1'],
                form.cleaned_data['ctry_code'],
                form.cleaned_data['number']
            )
            # generate a key and send a success email
            email_confirmation_key = generate_email_confirmation_key(
                user, key_only=True)
            profile = Profile(user=user, country_code=country_code,
                              phonenumber=phonenumber, email_activation_key=email_confirmation_key)
            if 'bitcoin_user' in request.session:
                profile.is_bitcoin_user = True
                del request.session['bitcoin_user']

            #get signup ip and location, stone insisted
            try:
                location = None
                user_ip = None
                user_ip = get_real_ip(request)

                if not user_ip:
                    print ':Get real ip failed'
                    user_ip = get_ip(request)

                print ':signup ip', str(user_ip)

                if user_ip is not None:
                    location = get_user_location(user_ip)
                    profile.signup_location = location
                print ':Signup location success'
            except Exception as e:
                print '::Get User IP Failed ', str(e)
            profile.save()
            user = authenticate(username=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # send email
                    email_verification_mail(
                        request, email, email_confirmation_key)
                    store_login_info(request)
                    return HttpResponseRedirect(settings.BASE_URL)
            else:
                error_message(request, 'signup')
        else:
            if 'This email is already in use.' in str(form.errors):
                error_message(request, 'signup_email')
            else:
                error_message(request, 'signup')
    return render_view(request, 'signup.html', {'form': form})




@logged_out_required
def signup2(request):
    '''
    handles the signup page
    @request  request object
    '''
    form = SignupForm2()
    if request.user.is_authenticated():
        return home_page(request)
    if request.method == "POST":
        post_values = request.POST.copy()

        form = SignupForm2(post_values)
        if form.is_valid():
            user = form.save()
            email, password = (
                form.cleaned_data['email'],
                form.cleaned_data['password1'],
                        )
            # generate a key and send a success email
            email_confirmation_key = generate_email_confirmation_key(
                user, key_only=True)
            profile = Profile(user=user, email_activation_key=email_confirmation_key)
            if 'bitcoin_user' in request.session:
                profile.is_bitcoin_user = True
                del request.session['bitcoin_user']

            #get signup ip and location, stone insisted
            try:
                location = None
                user_ip = None
                user_ip = get_real_ip(request)

                if not user_ip:
                    print ':Get real ip failed'
                    user_ip = get_ip(request)

                print ':signup ip', str(user_ip)

                if user_ip is not None:
                    location = get_user_location(user_ip)
                    profile.signup_location = location
                print ':Signup location success'
            except Exception as e:
                print '::Get User IP Failed ', str(e)
            profile.save()
            user = authenticate(username=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # send email
                    email_verification_mail(
                        request, email, email_confirmation_key)
                    store_login_info(request)
                    return HttpResponseRedirect(settings.BASE_URL)
            else:
                error_message(request, 'signup')
        else:
            if 'This email is already in use.' in str(form.errors):
                error_message(request, 'signup_email')
            else:
                error_message(request, 'signup')
    return render_view(request, 'join.html', {'form': form})



@logged_out_required
def recover_pass(request):
    '''
    edit user passords and profile
    @request  request object
    '''
    can_change_password = False
    if request.method == 'POST':
        form = RecoverPasswordForm(request.POST)
        if form.is_valid():
            email = request.POST['id_email']
            user = False
            try:
                user = User.objects.get(email=email)
            except Exception, e:
                pass
            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                template = settings.EMAIL_TEMPLATE_DIR + 'recoverpassword.html'
                c = {'tokenkey': token, 'uidb64':
                     uid, 'BASE_URL': settings.BASE_URL}
                mailer(
                    request, 'Remit Password Reset Instructions', template, c, email)
            success_message(
                request, 'password_recover_email', {'email': email})
            profile = Profile.objects.get(user=user)
            profile.recover_password = True
            profile.save()
        else:
            error_message(request, 'password_recover_email', {})
    return render_view(request, 'recover_password.html', {'can_change_password': can_change_password})


@logged_out_required
def recover_pass_confirm(request):
    '''
    edit user passords and profile
    @request  request object
    '''
    if not 'uid' in request.GET or not 'token' in request.GET:
        return HttpResponseRedirect(reverse('custom_404'))
    else:
        uidb64 = request.GET['uid']
        token = request.GET['token']
        uid = urlsafe_base64_decode(uidb64)
        user = User.objects.get(pk=uid)
        if user is not None and default_token_generator.check_token(user, token):
            can_change_password = True
            if request.method == 'POST':
                form = SetPasswordForm(user, request.POST)
                if form.is_valid():
                    form.save()
                    success_message(request, 'password_recover', {})
                    return HttpResponseRedirect(reverse('login'))
                else:
                    error_message(request, 'password_recover', {})
        else:
            return HttpResponseRedirect(reverse('custom_404'))
    return render_view(request, 'recover_password.html', {'can_change_password': can_change_password})


def add_landing_form_data(request):
    '''add data from the landing form'''
    if 'landing_send_form' in request.POST:
        form = landingSendForm(request.POST)
        if form.is_valid():
            try:
                data = request.POST
                extradata = {}
                number = data['receive_phone']
                extradata['ext'] = number[:2]
                extradata['number'] = number[2:]
                extradata['usdamount'] = data['send_currency']
                extradata['currencyamount'] = data['receive_currency']
                request.session['extradata'] = extradata
            except Exception, e:
                debug(e, 'Adding landingSendForm data', 'admin')
            return HttpResponseRedirect(reverse('login'))
    return HttpResponseRedirect(reverse('login'))


@logged_out_required
def signin(request):
    '''
    handles the signup page
    @request  request object
    '''
    auth_form = AuthenticationForm()
    form = AuthenticationForm()
    if request.method == 'POST':
        if 'bitcoin_user' in request.POST:
            request.session['bitcoin_user'] = True
        else:
            form = AuthenticationForm(request.POST)
            if form.is_valid():
                identification, password = (
                    form.cleaned_data['identification'],
                    form.cleaned_data['password'],
                )
                user = authenticate(username=identification,
                                    password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        if 'bitcoin_user' in request.session:
                            del request.session['bitcoin_user']
                            return HttpResponseRedirect(reverse('send_bitcoin'))
                        store_login_info(request)
                        return HttpResponseRedirect(reverse('home'))
                else:
                    error_message(request, 'login')
            else:
                error_message(request, 'login')
            # extradata =
    return render_view(request, 'login.html', {'form': form})


def email_verification_mail(request, email,
                            email_confirmation_key, update=False):
    '''send a verification email'''
    verification_link = '%saccount/%s' % (
        settings.ACTIVATION_LINK, email_confirmation_key)
    if update:
        verification_link = '%s?update=1' % verification_link
    template = '%semail_verification.html' % settings.EMAIL_TEMPLATE_DIR
    email_data = {'email': email,
                  'verification_link': verification_link,
                  'update': update,
                  }
    subject = 'Welcome to Remit, please verify your email address'
    if update:
        subject = 'Please verify your new Remit email address'
    return mailer(request, subject, template, email_data, email)


@login_required
def update_phonenumber(request):
    '''
    edit user passords and profile
    @request  request object
    '''
    if request.POST:
        form = updatePhonenumberForm()
    else:
        return HttpResponseRedirect(reverse('custom_404'))


@login_required
def account(request):
    '''
    edit user passords and profile
    @request  request object
    '''
    phonenumber_changed = False
    profile = Profile.objects.get(user=request.user)
    if request.POST:

        if 'new_password2' in request.POST:
            user_authenticated = True
            #form = SetPasswordForm(request.user, request.POST)
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                success_message(request, 'password_change')
            else:
                error_message(request, 'password_change')
        elif 'country_code' in request.POST:
            user_authenticated = True
            form = UpdatePhonenumberForm(request.POST)
            if form.is_valid():
                if not profile.country_code == request.POST['country_code'] or not profile.phonenumber == request.POST['phonenumber']:
                    profile.phone_verified = False
                    profile.country_code = request.POST['country_code']
                    profile.phonenumber = request.POST['phonenumber']
                    profile.save()
                    '''resend verification code'''
                    send_phone_verification_code(profile)
                    phonenumber_changed = True
            else:
                error_message(request, 'phonenumber_change')
        elif 'email' in request.POST:
            user_authenticated = True
            form = UpdateEmailForm(request.user, request.POST)
            if form.is_valid():
                email_confirmation_key = form.save()
                success_message(request, 'email_change')
                email_verification_mail(request,
                                        form.cleaned_data['email'], email_confirmation_key, update=True)
                # return HttpResponseRedirect(reverse('account'))
                request.user.email = form.cleaned_data['email']
            else:
                messages.error(
                    request, 'This email is already taken, please use another one')
        elif request.FILES and 'avatar' in request.FILES:
            user_authenticated = True
            form = UpdateAvatarForm(request.POST, request.FILES)
            if form.is_valid():
                profile.profile_pic = request.FILES['avatar']
                profile.save()
                # refresh the user
                profile = Profile.objects.get(user=request.user)
                messages.success(
                    request, "The profile picture was successfully updated")
            else:
                messages.error(request, form.errors)
        else:
            user_authenticated = access_restricted(request)

    else:
        user_authenticated = access_restricted(request)
    return render_view(request, 'account.html', {'user_authenticated': user_authenticated, 'phonenumber_changed': phonenumber_changed})


@login_required
def upload_passport(request):
    '''
    edit user passords and profile
    @request  request object
    '''
    if request.method == "POST":
        m = Profile.objects.get(user=request.user)
        if not 'passport' in request.FILES and m.id_pic:
            request.FILES['passport'] = m.id_pic
        form = PassportUploadForm(request.POST, request.FILES)
        if form.is_valid():
            update = m.id_pic
            m.id_pic = form.cleaned_data['passport']
            m.firstname = request.POST['firstname']
            m.lastname = request.POST['lastname']
            m.id_number = request.POST['id_number']
            m.dob = request.POST['dob'] = datetime.strptime(
                request.POST['dob_month'] + '-' + request.POST['dob_day'] + '-' + request.POST['dob_year'], '%m-%d-%Y')
            m.save()
            mail_template = 'user_verification'
            if update:
                mail_template = 'user_verification_update'
                messages.success(
                    request, "Your details were successfully updated")
            admin_mail(request, mail_template, m)
        else:
            print form.errors
            messages.error(request, form.errors)
    else:
        return HttpResponseRedirect(reverse('custom_404'))
    return HttpResponseRedirect(settings.BASE_URL)


def activate_email(request, name):
    '''
    activate an email
    @request  request object
    @name email hash
    '''
    profile = get_object_or_404(Profile.objects.filter(
        email_activation_key=name, email_activated=False),
        email_activation_key=name)
    if profile:
        # login the user if they are not logged in already
        if not request.user.is_authenticated():
            user = profile.user
            user = User.objects.get(pk=profile.user.pk)
            user.backend = 'accounts.backends.EmailVerificationBackend'
            user = authenticate(name=name)
            login(request, user)
        # Expire this link
        profile.email_activated = True
        profile.save()

        # send the phone activation sms
        if 'update' not in request.GET:
            send_phone_verification_code(profile)

        messages.success(
            request, "You have successfully verified your email address ")
        return HttpResponseRedirect(reverse('home'))


@ajax_required
def activate_sms(request, name):
    '''
    activate a phonenumber
    @request  request object
    @name email hash
    '''
    profile = False
    try:
        profile = Profile.objects.get(phone_activation_key=name)
    except Exception, e:
        print e
    if profile:
        # Expire this link
        profile.phone_verified = True
        profile.save()
        verified = True
        messages.success(request, "Your Phonenumber was successfully verified")
    else:
        verified = False

    template = settings.AJAX_TEMPLATE_DIR + 'verifiyphonenumber.html'
    html = render_to_string(
        template, {'verified': verified, 'BASE_URL': settings.BASE_URL})
    return HttpResponse(html)


@ajax_required
def resendcode(request, name):
    if name == 'phoneverificationcode':
        # change the user's phone number if they want that
        profile = Profile.objects.get(user=request.user)
        if request.GET.update:
            try:
                profile.country_code = request.GET['phone_ext']
                profile.phonenumber = request.GET['phone_num']
                profile.save()
            except Exception, e:
                print e
                debug(e, 'Resend phoneverificationcode error')
                pass
        # resend the phone code
    sent = send_phone_verification_code(profile)
    template = settings.AJAX_TEMPLATE_DIR + 'resendsms.html'
    html = render_to_string(
        template, {'sent': sent, 'number': profile.get_phonenumber()})
    return HttpResponse(html)


@ajax_required
def resend_verification_email(request):
    '''resend the verification email when user clicks resend button'''
    response = email = False
    email_confirmation_key = generate_email_confirmation_key(request.user)
    if email_confirmation_key:
        email = request.user.email
        if email_verification_mail(request, email, email_confirmation_key):
            response = True
    template = settings.AJAX_TEMPLATE_DIR + 'resend_verification_email.html'
    html = render_to_string(template, {'response': response, 'email': email})
    return HttpResponse(html)


@ajax_required
def send_verification_sms(request):
    profile = get_object_or_404(
        Profile.objects.filter(user=request.user), user=request.user)
    n = 4
    response = False
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    code = random.randint(range_start, range_end)
    profile.phone_activation_key = code
    profile.save()
    if profile.phone_activation_key == code:
        # send the sms
        template = settings.SMS_TEMPLATE_DIR + 'verificationsms.html'
        response = sendsms(profile.get_phonenumber(), template, {'code': code})
    html = render_to_string(template, {'response': response})
    return HttpResponse(html)


def send_phone_verification_code(profile):
    n = 4
    response = False
    try:
        code = profile.phone_activation_key
        if not code:
            range_start = 10 ** (n - 1)
            range_end = (10 ** n) - 1
            code = random.randint(range_start, range_end)
            profile.phone_activation_key = code
            profile.save()
        template = settings.SMS_TEMPLATE_DIR + 'verificationsms.html'
        response = sendsms(profile.get_phonenumber(), template, {'code': code})
    except Exception, e:
        debug(e, 'Resend Phonenumber Error')
    return response


@login_required
def userdetails_form(request):
    '''
    handles the userdetails
    @request  request object
    '''
    if request.method == "POST":
        post_values = request.POST.copy()
        try:
            profile = Profile.objects.get(user=request.user)
        except Exception, e:
            # create a new profile if one does not exist for this user
            profile = Profile(user=request.user)
            profile.save()
        form = UserDetailsForm(post_values, instance=profile)
        post_values['dob'] = datetime.strptime(
            post_values['dob_month'] + '-' + post_values['dob_day'] + '-' + post_values['dob_year'], '%m-%d-%Y')
        if form.is_valid():
            if form.save():
                profile.userdetails_provided = True
                profile.save()

                try:
                    user = User.objects.get(pk=request.user.pk)
                    user.firstname = post_values['firstname']
                    user.lastname = post_values['lastname']
                    user.save()
                except Exception, e:
                    print e
                return render_view(request, 'home.html', {'upload_id_form': True})
        else:
            messages.error(request, form.errors)
        return render_view(request, 'home.html', {})
    else:
        return HttpResponseRedirect(reverse('custom_404'))


def access_restricted(request):
    '''universal login for access restricted'''
    access_restricted = False
    if request.method == 'POST':
        form = AccessRestrictedForm(request.POST)
        if form.is_valid():
            if not request.user.check_password(form.cleaned_data['password']):
                error_message(request, 'access_restricted')
            else:
                access_restricted = True
        else:
            error_message(request, 'access_restricted')
    return access_restricted
