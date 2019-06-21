''' payment utils'''
import remit.settings as settings
from remit.utils import debug
from django.template.loader import render_to_string


def phone_extensions(country_code):
	country_code = int(country_code)
	extensions = {}
	extensions[254] = {'70', '71', '72', '73', '78','75'}
	extensions[256] = {'70', '72', '78', '73'}
	try:
		extensions = extensions[country_code]
	except Exception, e:
		print e
	return extensions

def format_sms_message(template, content):
	"""
	Format sms message that doesnt use
	background task.
	"""
	print ':Inside format_sms '
	content.update({
	    'BASE_URL': settings.BASE_URL,
	    'APP_NAME': settings.APP_NAME
	})



	message = render_to_string(template, content)
	message = message.encode('utf-8')

	print ':Sms message:: ', str(message)

	return message
