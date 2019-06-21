import remit.settings as settings
from django.template.loader import render_to_string


def clean_phonenumber(number):
    try:
        number = number.replace('-', '')
        number = number.replace(' ', '')
        number = number.replace(',', '')
    except Exception, e:
        debug(e, 'Error cleaning phonenumber %s' % number, 'sms')
    return number


def debug(error, message='', efile=''):
    from remit.utils import debug
    return debug(error, message, efile)


def nexmo_sms(message, to):
    from nexmo.libpynexmo.nexmomessage import NexmoMessage
    title = settings.NEXMO_FROM

    to = clean_phonenumber(to)

    try:
        if to[0] == 1:
            title = '12134657620'
    except Exception, e:
        debug(e, 'send sms error', 'sms')

    params = {
        'api_key': settings.NEXMO_USERNAME,
        'api_secret': settings.NEXMO_PASSWORD,
        'from': title,
        'to': '%s%s' % ('+', to),
        'text': message,
    }
    # print params
    sms = NexmoMessage(params)
    response = sms.send_request()
    return response


def twilio_sms(to, message):
    from twilio.rest import TwilioRestClient
    response = False
    to = clean_phonenumber(to)
    try:
        if not to[0] == '+':
            to = '%s%s' % ('+', to)
    except Exception, e:
        debug(e, 'Error sending twilio sms', 'sms')

    client = TwilioRestClient(
        settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    response = client.messages.create(
        body=message, to=to, from_='+16092574786')
    try:
        debug(e, 'Twilio sms response %s' % response, 'sms')
    except Exception, e:
        pass
    return response
