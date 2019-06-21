try:
    from hashlib import sha1 as sha_constructor, md5 as md5_constructor
except ImportError:
    from django.utils.hashcompat import sha_constructor, md5_constructor
import random
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import remit.settings as settings
from django.contrib import messages
import base64
from django.template import RequestContext
import sys
from django.contrib.gis.geoip import GeoIP
from datetime import datetime
from remit.tasks import send_email, send_sms
import cStringIO as StringIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from cgi import escape


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    result = StringIO.StringIO()
    #data = html.encode("ISO-8859-1")
    data = html.encode('utf-8')
    pdf = pisa.pisaDocument(StringIO.StringIO(data), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))


#@queue_command
def mailer(request, subject, template, content, to, sender=False):
    if settings.DISABLE_COMMS:
        return True
    if not sender:
        sender = settings.APP_EMAILS['info']
    try:
        content['STATIC_URL'] = settings.STATIC_URL
        html_content = render_to_string(
            template, content, context_instance=RequestContext(request))
        # this strips the html, so people will have the text as well.
        text_content = strip_tags(html_content)
        # create the email, and attach the HTML version as well.
        send_email(subject, text_content, sender, to, html_content)
    except Exception, e:
        print e
    return True


def admin_mail(request, code, data=False, e=False):
    '''admin email template'''
    template = settings.EMAIL_TEMPLATE_DIR + 'admin.html'
    subjects = {
        'pending_transaction': 'Pending Transaction',
        'complete_transaction': 'Transaction Complete',
        'user_verification': 'User Pending Verification',
        'user_verification_update': 'User Updated Verification Details',
        'new_user': '',
        'rates_error': 'An error occurred while fetching the rates',
        'server_error': 'Dude your App Just Broke',
        'contact_us': 'New Contact Message',
    }
    if settings.DEBUG:
        emails = settings.DEBUG_EMAILS
    if code == 'server_error':
        emails = {'mandelashaban593@gmail.com'}
    elif code == 'contact_us':
        emails = {'mandelashaban593@gmail.com'}
    else:
        emails = {'mandelashaban593@gmail.com'}
    response = False
    if code in subjects:
        #emails = {'madra@redcore.co.ug'}
        subject = subjects[code]
        extradata = {}
        extradata['data'] = data
        extradata['code'] = code
        # if e:
        #    extradata['e'] = repr(e)
        sender = settings.APP_EMAILS['info']
        if 'contact_us' in subjects:
            sender = settings.APP_EMAILS['contact_us']
        for email in emails:
            response = mailer(request, subject, template,
                              extradata, email, sender)
    return response


def error_message(request, msgtype, data={}):
    template = settings.BASE_DIR + 'templates/error_messages.html'
    data['type'] = msgtype
    text = render_to_string(
        template, data, context_instance=RequestContext(request))
    messages.error(request, text)


def success_message(request, msgtype, data={}):
    template = settings.BASE_DIR + 'templates/success_messages.html'
    data['type'] = msgtype
    text = render_to_string(
        template, data, context_instance=RequestContext(request))
    messages.success(request, text)


def sendsms(to, template, content):
    '''backward compatibility ,move this to tasks.py'''

    send_sms(to, template, content)
    return True


def generate_sha1(string, salt=None):
    """
    Generates a sha1 hash for supplied string. Doesn't need to be very secure
    because it's not used for password checking. We got Django for that.

    :param string:
        The string that needs to be encrypted.

    :param salt:
        Optionally define your own salt. If none is supplied, will use a random
        string of 5 characters.

    :return: Tuple containing the salt and hash.

    """
    if not isinstance(string, (str, unicode)):
        string = str(string)
    if not salt:
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
    hash = sha_constructor(salt + str(string.encode('utf-8'))).hexdigest()

    return (salt, hash)


def urlsafe_base64_encode(s):
    """
    Encodes a bytestring in base64 for use in URLs, stripping any trailing
    equal signs.
    """
    return base64.urlsafe_b64encode(s).rstrip(b'\n=')


def urlsafe_base64_decode(s):
    """
    Decodes a base64 encoded string, adding back any trailing equal signs that
    might have been stripped.
    """
    s = s.encode('utf-8')  # base64encode should only return ASCII.
    try:
        return base64.urlsafe_b64decode(s.ljust(len(s) + len(s) % 4, b'='))
    except (LookupError, BinasciiError) as e:
        raise ValueError(e)


def debug(e, txt=False, log='debug'):
    if settings.LOCALHOST:
        if not txt:
            txt = ''
        print >> sys.stderr, 'Debuging____________________ %s' % txt
        print >> sys.stderr, e
    else:
        try:
            old_stdout = sys.stdout
            log_file = open("%slogs/%s.log" % (settings.BASE_DIR, log), "a")
            sys.stdout = log_file
            print '%s: Debuging____________________ %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                           txt)
            print e
            sys.stdout = old_stdout
            log_file.close()
        except Exception, e:
            pass


def unregistered_number_communication(request, number, email, mtn):
    '''communicate with unregistered user'''
    sms_response = mtn.kyc_sms(number)
    email_response = mtn.kyc_email(number, email, request)
    print "send sms to %s , response %s" % (number, sms_response)
    print "send email to %s , response %s" % (email, email_response)


def check_verified_number(request, number, email):
    registered = {'valid': False}
    if settings.DISABLE_MTN:
        registered = {'valid': True}
    else:
        if get_mobile_network_code(number) == 'MTN':
            from payments.mtn import Mtn
            mtn = Mtn()
            registered['valid'] = False
            try:
                result, response = mtn.momo_check(number)
                if 'error' in response:
                    registered['has_error'] = True
                else:
                    if result:
                        kyc_response = mtn.kyc_check(number)
                        registered['valid_momo'] = result
                        registered['valid_kyc'] = kyc_response
                        registered['valid'] = kyc_response
                        if not kyc_response:
                            '''send kyc message'''
                            mtn.kyc_sms(number)
                    else:
                        '''send momo message'''
                        mtn.momo_sms(number)
            except Exception:
                pass
    return registered


def get_mobile_network_code(number):
    '''get mobile code'''
    code = False
    number = str(number)
    number = number[:2]
    network_code = {}
    network_code['MTN'] = ['77', '78']
    network_code['UTL'] = ['71']
    network_code['AIRTEL'] = ['70', '75']
    if number in network_code['MTN']:
        code = 'MTN'
    elif number in network_code['AIRTEL']:
        code = 'AIRTEL'
    elif number in network_code['UTL']:
        code = 'UTL'
    return code

COUNTRY_CHOICES = (
    ('UG', 'Uganda'),
    ('KE', 'Kenya'),
    ('TZ', 'Tanzania'),
    ('RW', 'Rwanda'),
)



NETWORK_CHOICES = (
    ('MTN', 'MTN Mobile Money'),
    ('AIRTEL', 'Airtel Money'),
    ('UTL', 'M-Sente'),
)


def check_phonebook(post_values):
    from remit.models import Phonebook
    '''check if a number exists in a phonebook'''
    try:
        check_phonebook = Phonebook.objects.get(
            ext=post_values['ext'],
            number=post_values['number'],
            # firstname=post_values['firstname'],
            # lastname=post_values['lastname'],
            user=post_values['user'],
            country_code=post_values['country_code'],
        )
        return check_phonebook
    except Exception, e:
        return False


def get_site_admin():
    '''fetch the site admin user'''
    from django.contrib.auth.models import User
    admin = User.objects.get(pk=settings.PROCESSED_BY)
    return admin


def log_unauthorized_access(request):
    debug(request, 'log_unauthorized_access')


def recipient_country_code(request, remove_session=False):
    '''get the recipient country code'''
    country_code = False
    country = request.session.get('country', None)
    if country:
        try:
            country_code = COUNTRY_CODE[country]
        except Exception, e:
            print e
        if remove_session:
            del request.session['country']
    return country_code


def recipient_currency(country):
    '''
    extend this to format to default currency
    '''
    debug(country)
    to_curr = 'UGX'
    try:
        to_curr = CURRENCIES[country]
    except Exception, e:
        pass
    return to_curr

CURRENCIES = {
    'KE': 'KES',
    'UG': 'UGX',
    'RW': 'RWF'
}

COUNTRY_CODE = {
    'KE': 254,
    'UG': 256,
    'RW': 250
}

COUNTTRY_CODE = {
    'KE': 254,
    'UG': 256,
    'RW': 250
}

def country_extensions(code=False):
    exts = {}
    # kenya
    exts['KE'] = {
        'safaricom': ['70', '71', '72'],
        'airtel': ['73', '78']
    }
    exts['UG'] = {
        'mtn': ['77', '78'],
        'airtel': ['70', '75']
    }
    exts['RW'] = {
        'mtn': ['78'],
        # 'airtel': ['73'],
        # 'tigo': ['72']
    }
    if code in exts:
        return exts[code]
    return exts


def random_string_generator(string_len):
    """
    generate random string with length "string_len"
    """
    import string
    import random

    random_string = ''.join(random.choice(string.ascii_uppercase)
                            for i in range(string_len))
    return random_string

"""
def sample_mail(subject,data,recipient):
    '''temp email send'''
    if subject is not None:
        send_mail(subject,str(data),settings.EMAIL_HOST_USER,[recipient],fail_silently=False)

        return True

    else:
        return False
"""


def remove_non_digits(x):
    import re
    re.sub("\D", "", x)
    return x

def get_user_location(ip_address):
    """Use ip address to get user location."""
    location_data = {}
    location_data['ip_address'] = ip_address

    try:
        print ':IP address ', str(ip_address)
        geo = GeoIP()
        location = geo.city(ip_address)
        location_data['location'] = location
        print '::Location data ',str(location_data)
        #location_data['ip_address'] = ip_address
        print ':Location data success'
        debug('user location success', 'get_user_location failed', 'debug')
    except Exception as e:
        debug(e, 'get_user_location failed', 'debug')
        print ':Location data failed ', str(e)

    return location_data
