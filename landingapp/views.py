# Create your views here.
'''landingapp views'''
from django.template import RequestContext
from django.shortcuts import HttpResponse, render_to_response, \
    HttpResponseRedirect, render
from remit.decorators import logged_out_required
from accounts.forms import SignupForm,SignupForm2, AuthenticationForm, \
    UserDetailsForm, AccessRestrictedForm, VerifyPhoneForm, \
    PassportUploadForm, RecoverPasswordForm, SetPasswordForm, \
    landingSendForm, PasswordChangeForm, UpdatePhonenumberForm, \
    UpdateEmailForm, UpdateAvatarForm
from accounts.models import Profile,Create_staff_User  
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from landingapp.forms import ContactUsForm
from remit.utils import admin_mail, recipient_country_code, \
    debug, remove_non_digits
from django.contrib import messages
from remit.models import Country, Charge
from django.conf import settings
from django.contrib.sites.models import Site
from accounts.models import Profile
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from remit_admin.models import HealthInfo, LawhInfo, JounalisthInfo,EducationInfo


def render_view(request, template, data):
    '''
    wrapper for rendering views , loads RequestContext
    @request  request object
    @template  string
    @data  tumple
    '''
    template = "v2/%s" % template
    data['STATIC_URL'] = '%sv2/' % settings.STATIC_URL
    return render_to_response(
        template, data,
        context_instance=RequestContext(request)
    )


@logged_out_required
def landing_page(request, country=False):
    '''
    handles the index page , loads homepage when user is logged in
    @request  request object
    '''
    sendmoneyform = False
    form = landingSendForm()
    country_code = 256
    
    

    landingformdata = {}

    
    landingformdata = {
      
    }
    sendamount = 100
    receiveamount = 00
    rates = 00
    

    if request.POST:
        form = landingSendForm(request.POST)
        if form.is_valid():
            try:
                data = request.POST
                extradata = {}
                ext = data['countrycode']
                mobilenumber = data['mobile_number']
                mobilenumber = remove_non_digits(mobilenumber)
                mobilenumber = mobilenumber[4:]
                extradata['ext'] = ext
                extradata['number'] = mobilenumber
                extradata['usdamount'] = data['sendamount']
                receiveamount = data['receiveamount']
                receiveamount = remove_non_digits(receiveamount)
                extradata['currencyamount'] = receiveamount
                request.session['extradata'] = extradata
                sending_amount = int(data['sendamount'])
                if sending_amount > int(rates.transfer_limit_usd) or sending_amount < int(rates.transfer_minimum_usd):
                    form.add_error(
                        'sendamount', "Please specifiy an amount less than %s and greater tha %s" % (
                            rates.transfer_limit_usd,
                            rates.transfer_minimum_usd)
                    )
                else:
                    return HttpResponseRedirect(reverse('login'))
            except Exception, e:
                debug(e, 'Adding landingSendForm data', 'admin')
        else:
            print form.errors

    return render_view(request, 'index.html', {'rates': rates})
    
    
                       

#@cache_page(60 * 15)


def faq(request):
    '''
    faq page
    @request  request object
    '''
    rates = Site.objects.get_current().rate
    return render_view(request, 'faq.html', {'rates': rates})

#@cache_page(60 * 15)


def tos(request):
    '''
    Terms of Service
    @request  request object
    '''
    return render_view(request, 'tos.html', {})

#@cache_page(60 * 15)


def contact_us(request):
    '''
    Contact Us
    @request  request object
    '''
    form = ContactUsForm()
    if request.POST:
        form = ContactUsForm(request.POST)
        if form.is_valid():
            admin_mail(request, 'contact_us', request.POST)
            messages.success(
                request, "Thank you for contacting us. We have received your message and we shall get back to you shortly.")
    return render_view(request, 'contactus.html', {'form': form})

#@cache_page(60 * 15)



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




def policy(request):
    '''
    privacy policy
    @request  request object
    '''
    return render_view(request, 'policy.html', {})

def rate(request):
    '''
    rate
    @request  request object
    '''
    return render_view(request, 'rate.html', {})

#@cache_page(60 * 15)


def how_remit_works(request):
    '''
    how remit works
    @request  request object
    '''
    return render_view(request, 'how_remit_works.html', {})

#@cache_page(60 * 15)


def about_us(request):
    '''
    About B-Link
    @request  request object
    '''
    return render_view(request, 'about_us.html', {})

def history(request):
    '''
    History of blink
    @request  request object
    '''
    return render_view(request, 'history.html', {})
    
def careers(request):
    '''
    Careers
    @request  request object
    '''
    return render_view(request, 'careers.html', {}) 

def publications(request):
    '''
    Publications
    @request  request object
    '''
    pub_info = JounalisthInfo.objects.all()
    return render_view(request, 'publications.html', {'pub_info':pub_info})

def statistics(request):
    '''
    Statistics
    @request  request object
    '''
    return render_view(request, 'statistics.html', {})

def legislation(request):
    '''
    Legislation
    @request  request object
    '''
    law_info = LawhInfo.objects.all()

    return render_view(request, 'legislation.html', {'law_info':law_info})

def funding(request):
    '''
    Funding
    @request  request object
    '''
    return render_view(request, 'funding.html', {})

def econsult(request):
    '''
    E-consult
    @request  request object
    '''
    return render_view(request, 'e-consult.html', {})

def members(request):
    '''
    Members
    @request  request object
    '''
    return render_view(request, 'members.html', {})

def districts(request):
    '''
    Districts
    @request  request object
    '''
    return render_view(request, 'districts.html', {})

def forums(request):
    '''
    Members
    @request  request object
    '''
    return render_view(request, 'forums.html', {})
    
def support(request):
    '''
    Members
    @request  request object
    '''
    return render_view(request, 'support.html', {})
    
def education(request):
    '''
    Education
    @request  request object
    '''
    educ_info = EducationInfo.objects.all()
    return render_view(request, 'education.html', {'educ_info':educ_info})

def disaster(request):
    '''
    Disaster
    @request  request object
    '''
    return render_view(request, 'disaster.html', {})

def health(request):
    '''
    Health
    @request  request object
    '''
    health_info = HealthInfo.objects.all()

    return render_view(request, 'health.html', {'health_info':health_info})

def livelihood(request):
    '''
    Livelihood
    @request  request object
    '''
    return render_view(request, 'livelihood.html', {})

def healthcare(request):
    '''
    Healthcare
    @request  request object
    '''
    return render_view(request, 'healthcare.html', {})

def civics(request):
    '''
    civics
    @request  request object
    '''
    return render_view(request, 'civics.html', {})  

def join(request):
    '''
    Join
    @request  request object
    '''
    return render_view(request, 'join.html', {})

def support(request):
    '''
    Support
    @request  request object
    '''
    return render_view(request, 'support.html', {})

def donate(request):
    '''
    Donate
    @request  request object
    '''
    from payments.cc import prepare_cc_url
    
    cc_link = prepare_cc_url(request, transaction)

    return render_view(request, 'donate.html', {})

def policiesandissues(request):
    '''
    Policies and Issues
    @request  request object
    '''
    return render_view(request, 'policiesandissues.html', {})

def diseasesandconditions(request):
    '''
    Diseases and Conditions
    @request  request object
    '''
    return render_view(request, 'diseasesandconditions.html', {})

def costfinancing(request):
    '''
    Costs and Financing
    @request  request object
    '''
    return render_view(request, 'costfinancing.html', {})

def medicaldirectory(request):
    '''
    Medical Directory
    @request  request object
    '''
    return render_view(request, 'medicaldirectory.html', {})

def Hiv_Aids(request):
    '''
    Medical Directory
    @request  request object
    '''
    return render_view(request, 'Hiv_Aids.html', {})


def login(request):
    '''
    Login
    @request  request object
    '''
    return render_view(request, 'login.html', {})

def root_file(request, filename, content_type, img=False):
    '''
    load a file e.g robots.txt , sitemap.xml
    @request  request object
    '''
    if img:
        img = "%s/%s" % (settings.STATIC_ROOT, filename)
        image_data = open(img, "rb").read()
        return HttpResponse(image_data, content_type="image/png")
    return render(request, filename,
                  {}, content_type=content_type
                  )


def clinics(request):
    '''
    E-consult
    @request  request object
    '''
    ch = ''
    user_list1 = ''
    try:
        user_list = Create_staff_User.objects.filter(category="clinics")
        for ch in user_list:
            print ch.cat_name

    except Exception, e:
        
        user_list1 = Create_staff_User.objects.get(category="clinics")
        print user_list1.cat_name


    debug(ch, 'stuff')
   
    # search query
    if 'q' in request.GET:
        pretitle += ' | %s' % request.GET['q']
        page_title += ' | %s' % request.GET['q']
        user_list = user_list.filter(
            Q(username__icontains='' + request.GET['q'] + ''))
        user_list1 = user_list1.filter(
            Q(username__icontains='' + request.GET['q'] + ''))

    paginator = Paginator(user_list, settings.PAGNATION_LIMIT)
    paginator1 = Paginator(user_list1, settings.PAGNATION_LIMIT)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
        users1 = paginator1.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users = paginator.page(1)
        users1 = paginator1.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users = paginator.page(paginator.num_pages)
        users1 = paginator1.page(paginator1.num_pages)
    return render_view(request, 'clinics.html', {'users': users, 'users1': users1})


def hospitals(request):
    '''
    E-consult
    @request  request object
    '''
    ch = ''
    user_list1 = ''
    try:
        user_list = Create_staff_User.objects.filter(category="hospitals")
        for ch in user_list:
            print ch.cat_name

    except Exception, e:
        
        user_list1 = Create_staff_User.objects.get(category="hospitals")
        print user_list1.cat_name


    debug(ch, 'stuff')
   
    # search query
    if 'q' in request.GET:
        pretitle += ' | %s' % request.GET['q']
        page_title += ' | %s' % request.GET['q']
        user_list = user_list.filter(
            Q(username__icontains='' + request.GET['q'] + ''))
        user_list1 = user_list1.filter(
            Q(username__icontains='' + request.GET['q'] + ''))

    paginator = Paginator(user_list, settings.PAGNATION_LIMIT)
    paginator1 = Paginator(user_list1, settings.PAGNATION_LIMIT)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
        users1 = paginator1.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users = paginator.page(1)
        users1 = paginator1.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users = paginator.page(paginator.num_pages)
        users1 = paginator1.page(paginator1.num_pages)
    return render_view(request, 'hospitals.html', {'users': users, 'users1': users1})





def labs(request):
    '''
    E-consult
    @request  request object
    '''
    ch = ''
    user_list1 = ''
    try:
        user_list = Create_staff_User.objects.filter(category="labs")
        for ch in user_list:
            print ch.cat_name

    except Exception, e:
        
        user_list1 = Create_staff_User.objects.get(category="labs")
        print user_list1.cat_name


    debug(ch, 'stuff')
   
    # search query
    if 'q' in request.GET:
        pretitle += ' | %s' % request.GET['q']
        page_title += ' | %s' % request.GET['q']
        user_list = user_list.filter(
            Q(username__icontains='' + request.GET['q'] + ''))
        user_list1 = user_list1.filter(
            Q(username__icontains='' + request.GET['q'] + ''))

    paginator = Paginator(user_list, settings.PAGNATION_LIMIT)
    paginator1 = Paginator(user_list1, settings.PAGNATION_LIMIT)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
        users1 = paginator1.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users = paginator.page(1)
        users1 = paginator1.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users = paginator.page(paginator.num_pages)
        users1 = paginator1.page(paginator1.num_pages)
    return render_view(request, 'labaratories.html', {'users': users, 'users1': users1})


def doctors(request):
    '''
    E-consult
    @request  request object
    '''
    ch = ''
    user_list1 = ''
    try:
        user_list = Create_staff_User.objects.filter(category="doctors")
        for ch in user_list:
            print ch.cat_name

    except Exception, e:
        
        user_list1 = Create_staff_User.objects.get(category="doctors")
        print user_list1.cat_name


    debug(ch, 'stuff')
   
    # search query
    if 'q' in request.GET:
        pretitle += ' | %s' % request.GET['q']
        page_title += ' | %s' % request.GET['q']
        user_list = user_list.filter(
            Q(username__icontains='' + request.GET['q'] + ''))
        user_list1 = user_list1.filter(
            Q(username__icontains='' + request.GET['q'] + ''))

    paginator = Paginator(user_list, settings.PAGNATION_LIMIT)
    paginator1 = Paginator(user_list1, settings.PAGNATION_LIMIT)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
        users1 = paginator1.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users = paginator.page(1)
        users1 = paginator1.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users = paginator.page(paginator.num_pages)
        users1 = paginator1.page(paginator1.num_pages)
    return render_view(request, 'doctors.html', {'users': users, 'users1': users1})


def clinic_name(request):
    '''
    E-consult
    @request  request object
    '''
    user_list1 = ''
    try:
        user_list = Create_staff_User.objects.filter(category="clinics")
        for ch in user_list:
            print ch.cat_name

    except Exception, e:
        
        user_list1 = Create_staff_User.objects.get(category="clinics")
        print user_list1.cat_name


    debug(ch, 'stuff')
   
    # search query
    if 'q' in request.GET:
        pretitle += ' | %s' % request.GET['q']
        page_title += ' | %s' % request.GET['q']
        user_list = user_list.filter(
            Q(username__icontains='' + request.GET['q'] + ''))
        user_list1 = user_list1.filter(
            Q(username__icontains='' + request.GET['q'] + ''))

    paginator = Paginator(user_list, settings.PAGNATION_LIMIT)
    paginator1 = Paginator(user_list1, settings.PAGNATION_LIMIT)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
        users1 = paginator1.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users = paginator.page(1)
        users1 = paginator1.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users = paginator.page(paginator.num_pages)
        users1 = paginator1.page(paginator1.num_pages)
    return render_view(request, 'clinics.html', {'users': users, 'users1': users1})

def nurse_home(request):
    '''
    E-consult
    @request  request object
    '''
    ch = ''
    user_list1 = ''
    try:
        user_list = Create_staff_User.objects.filter(category="clinics")
        for ch in user_list:
            print ch.cat_name

    except Exception, e:
        
        user_list1 = Create_staff_User.objects.get(category="clinics")
        print user_list1.cat_name


    debug(ch, 'stuff')
   
    # search query
    if 'q' in request.GET:
        pretitle += ' | %s' % request.GET['q']
        page_title += ' | %s' % request.GET['q']
        user_list = user_list.filter(
            Q(username__icontains='' + request.GET['q'] + ''))
        user_list1 = user_list1.filter(
            Q(username__icontains='' + request.GET['q'] + ''))

    paginator = Paginator(user_list, settings.PAGNATION_LIMIT)
    paginator1 = Paginator(user_list1, settings.PAGNATION_LIMIT)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
        users1 = paginator1.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        users = paginator.page(1)
        users1 = paginator1.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        users = paginator.page(paginator.num_pages)
        users1 = paginator1.page(paginator1.num_pages)
    return render_view(request, 'nurse_home.html', {'users': users, 'users1': users1})





def clinic_spec(request):

    if request.POST:
        name = request.POST['q']
       
        transaction = get_object_or_404(Create_staff_User.objects.filter(cat_name=name))

        #log_action(request,model_object=transaction, action_flag=6, change_message='Downloaded Receipt Transaction')
        return render_view(request, 'clinics_spec.html', {'data': transaction})

    return render_view(request, 'clinics_search.html', {})

def hospitals_spec(request):

    if request.POST:
        name = request.POST['q']
       
        transaction = get_object_or_404(Create_staff_User.objects.filter(cat_name=name))

        #log_action(request,model_object=transaction, action_flag=6, change_message='Downloaded Receipt Transaction')
        return render_view(request, 'hospitals_spec.html', {'data': transaction})

    return render_view(request, 'hospitals_search.html', {})


def nurse_spec(request):

    if request.POST:
        name = request.POST['q']
       
        transaction = get_object_or_404(Create_staff_User.objects.filter(cat_name=name))

        #log_action(request,model_object=transaction, action_flag=6, change_message='Downloaded Receipt Transaction')
        return render_view(request, 'nurse_spec.html', {'data': transaction})

    return render_view(request, 'nurse_search.html', {})



def labs_spec(request):

    if request.POST:
        name = request.POST['q']
       
        transaction = get_object_or_404(Create_staff_User.objects.filter(cat_name=name))

        #log_action(request,model_object=transaction, action_flag=6, change_message='Downloaded Receipt Transaction')
        return render_view(request, 'labs_spec.html', {'data': transaction})

    return render_view(request, 'labs_search.html', {})

def clinic_locate(request):

    if request.POST:
        name = request.POST.get('name', None)
       
        transaction = get_object_or_404(Create_staff_User.objects.filter(districts=name))

        #log_action(request,model_object=transaction, action_flag=6, change_message='Downloaded Receipt Transaction')
        return render_view(request, 'clinic_locate.html', {'data': transaction})

    return render_view(request, 'clinic_locate.html', {})


def hospitals_locate(request):

    if request.POST:
        name = request.POST.get('name', None)
       
        transaction = get_object_or_404(Create_staff_User.objects.filter(districts=name))

        #log_action(request,model_object=transaction, action_flag=6, change_message='Downloaded Receipt Transaction')
        return render_view(request, 'hospitals_locate.html', {'data': transaction})

    return render_view(request, 'hospitals_locate.html', {})




def labs_locate(request):

    if request.POST:
        name = request.POST.get('name', None)
       
        transaction = get_object_or_404(Create_staff_User.objects.filter(districts=name))

        #log_action(request,model_object=transaction, action_flag=6, change_message='Downloaded Receipt Transaction')
        return render_view(request, 'labs_locate.html', {'data': transaction})

    return render_view(request, 'labs_locate.html', {})

def nurse_locate(request):

    if request.POST:
        name = request.POST.get('name', None)
       
        transaction = get_object_or_404(Create_staff_User.objects.filter(districts=name))

        #log_action(request,model_object=transaction, action_flag=6, change_message='Downloaded Receipt Transaction')
        return render_view(request, 'nurse_locate.html', {'data': transaction})

    return render_view(request, 'nurse_locate.html', {})





def nurse_search(request):

    if request.POST:
        name = request.POST.get('name', None)
       
        transaction = get_object_or_404(Create_staff_User.objects.filter(districts=name))

        #log_action(request,model_object=transaction, action_flag=6, change_message='Downloaded Receipt Transaction')
        return render_view(request, 'nurse_locate.html', {'data': transaction})

    return render_view(request, 'nurse_locate.html', {})


def labs_region(request):

    if request.POST:
        name = request.POST.get('name', None)
       
        transaction = get_object_or_404(Create_staff_User.objects.filter(region=name))

        #log_action(request,model_object=transaction, action_flag=6, change_message='Downloaded Receipt Transaction')
        return render_view(request, 'labs_region.html', {'data': transaction})

    return render_view(request, 'labs_region.html', {})


def nurse_region(request):

    if request.POST:
        name = request.POST.get('name', None)
       
        transaction = get_object_or_404(Create_staff_User.objects.filter(region=name))

        #log_action(request,model_object=transaction, action_flag=6, change_message='Downloaded Receipt Transaction')
        return render_view(request, 'nurse_region.html', {'data': transaction})

    return render_view(request, 'nurse_region.html', {})


def clinic_region(request):

    if request.POST:
        name = request.POST.get('name', None)
       
        transaction = get_object_or_404(Create_staff_User.objects.filter(region=name))

        #log_action(request,model_object=transaction, action_flag=6, change_message='Downloaded Receipt Transaction')
        return render_view(request, 'clinic_region.html', {'data': transaction})

    return render_view(request, 'clinic_region.html', {})


def hospitals_region(request):

    if request.POST:
        name = request.POST.get('name', None)
       
        transaction = get_object_or_404(Create_staff_User.objects.filter(region=name))

        #log_action(request,model_object=transaction, action_flag=6, change_message='Downloaded Receipt Transaction')
        return render_view(request, 'hospitals_region.html', {'data': transaction})

    return render_view(request, 'hospitals_region.html', {})



def dentist(request):
        name = request.POST.get('name', None)
        record = True

        try:

            transaction = Create_staff_User.objects.get(cat_name=name)
        except Exception, e:
            print "Record does exist"
            record = False
            transaction = None


        return render_view(request, 'dentist.html', {'data': transaction})

def surgeon(request):
        name = request.POST.get('name', None)
        record = True
        try:

            transaction = Create_staff_User.objects.get(cat_name=name)
        except Exception, e:
            print "Record does exist"
            record = False
            transaction = None

       
        transaction = Create_staff_User.objects.get(cat_name=name)
        return render_view(request, 'surgeon.html', {'data': transaction,'record':record})


def  gen_doctor(request):
        name = request.POST.get('name', None)
        record = True

        try:

            transaction = Create_staff_User.objects.get(cat_name=name)
        except Exception, e:
            print "Record does exist"
            record = False
            transaction = None
       
        
        return render_view(request, 'gen_doctor.html', {'data': transaction,'record':record})






def clinic_search(request):
        name = request.POST['name']

        try:

            transaction = Create_staff_User.objects.get(cat_name=name)

            print "Clinic Id %s " % transaction.id

        except Exception, e:
            print "Record does exist"
           
            transaction = None

       
        return render_view(request, 'nurse_search.html', {'data': transaction})

        


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
    context= {'form':form}
  
    return render_to_response("v2/payment.html", context)