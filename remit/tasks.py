'''background tasks'''
from django.core.mail import EmailMultiAlternatives
from background_task import background
import remit.settings as settings
from django.template.loader import render_to_string
from remit.sms import twilio_sms, nexmo_sms


def debug(error, message='', efile=''):
    """debug errors."""
    from remit.utils import debug
    return debug(error, message, efile)


@background(schedule=40)
def send_email(subject, text_content, sender, receipient, html_content):
    """schedule email sending."""
    if settings.DISABLE_COMMS:
        return True
    msg = EmailMultiAlternatives(subject, text_content, sender, [receipient])
    msg.attach_alternative(html_content,  "text/html")
    print "sent mail from %s to %s" % (sender, receipient)
    return msg.send()


@background(schedule=40)
def send_sms(to, template, content, message=False):
    """send sms."""
    if settings.DISABLE_COMMS:
        return True
    content.update({
        'BASE_URL': settings.BASE_URL,
        'APP_NAME': settings.APP_NAME
    })
    if not message:
        message = render_to_string(template, content)
        message = message.encode('utf-8')

        print ':=send_sms message: ', message

    response = {}
    num = "%s" % to

    try:
        if settings.USE_TWILIO:
            """Use twilio for all numbers."""
            response = twilio_sms(to, message)
        else:
            if num[0] == '1':
                '''use twilio for American Numbers'''
                response = twilio_sms(to, message)
            else:
                response = nexmo_sms(message, to)
    except Exception as e:
        debug(e, 'send_sms twilio,nexmo switch error', 'sms')



    # if num[0] == '1':
    #     '''use twilio for American Numbers'''
    #     response = twilio_sms(to, message)
    # else:
    #     response = nexmo_sms(message, to)
    return response
