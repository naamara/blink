'''yo pay'''
import remit.settings as settings
from datetime import datetime
import requests
from BeautifulSoup import BeautifulSoup
from remit.utils import debug
from xml.sax.saxutils import escape
from xml.sax.saxutils import quoteattr
import json
import xmltodict


class yopay():
	"""Handle payments for YoPay"""

	NETWORK = {
	'MTN_UG' : 'MTN_UGANDA',
	'AIRTEL_UG': 'AIRTEL_UGANDA',
	'WARID_UG' : 'WARID_UGANDAPESA',
	} 


	def __init__(self):
		self.api_username = settings.YOPAY_USERNAME
		self.api_password = settings.YOPAY_PASSWORD
		self.api_endpoint = settings.YOPAY_ENDPOINT
		

	def send_xml_request(self, xml):
		'''
		send the xml
		'''
		response = {'status':'error', 'statuscode':9999, 'statusmessage':'', 'errormessage':'', 'transactionstatus':'', 'transactionreference':''}
		headers = {'Content-Type': 'application/xml'}
		
		try:
			r = requests.post(self.api_endpoint, data=xml, headers=headers,verify=False)
			data = xmltodict.parse(r.text)
			data = dict(data['AutoCreate']['Response'])
			response = dict((k.lower(), v) for k, v in data.iteritems())
		except Exception, e:
			debug(e, 'send_xml_request error','yo')
			response['statusmessage'] = 'Server Connection error'
			response['errormessage'] = e
			return response
		debug(response,'Yo response')
		return response


	def deposit(self, amount, phone_number, narrative, ref_text):
		"""
		* Deposit funds into Yo! Payments account from a phone's Mobile Money account 
		* @param float  amount The amount of money to deposit
		* @param string phone_number Phone number to pull Mobile Money from <br> [Format]: 256772123456
		* @param string narrative A description of the transaction 
		* @param string ref_text The text to be returned to the user's phone after the transaction is complete
		* 
		* @return xml The XML Request String to be sent to the Yo! Payments Server
		*
		* ------------------------------------------------------------------------------------------------------------------
		*
		"""
		xml_request = "<?xml version='1.0' encoding='UTF-8'?><AutoCreate><Request><APIUsername>%s</APIUsername><APIPassword>%s</APIPassword><Method>acdepositfunds</Method><NonBlocking>FALSE</NonBlocking><Amount>%s</Amount><Account>%s</Account><Narrative>%s</Narrative><ProviderReferenceText>%s</ProviderReferenceText></Request></AutoCreate>"%(self.api_username, self.api_password, amount, phone_number, narrative, ref_text)
		return self.send_xml_request(xml_request)


	def withdraw(self, amount, phone_number, ref_text, narrative="Remit.ug"):
		"""
		* Withdraw funds from Yo! Payments account and add to a phone's Mobile Money account
		* @param float  amount The amount of money to deposit
		* @param string phone_number Phone number to pull Mobile Money from <br> [Format]: 256772123456
		* @param string narrative A description of the transaction 
		* @param string ref_text The text to be returned to the user's phone after the transaction is complete
		* 
		* @return xml The XML Request String to be sent to the Yo! Payments Server
		*
		* ------------------------------------------------------------------------------------------------------------------
		*
		"""
		'''
		we vary the external reference , this seems to solve the duplicate transaction error
		'''
		ref_text = quoteattr(escape(ref_text))
		ext_ref_text = " %s : %s "%(ref_text, datetime.now())
		xml_request = '<?xml version="1.0" encoding="UTF-8"?><AutoCreate><Request><APIUsername>%s</APIUsername><APIPassword>%s</APIPassword><Method>acwithdrawfunds</Method><NonBlocking>FALSE</NonBlocking><Amount>%s</Amount><Account>%s</Account><Narrative>%s</Narrative><ProviderReferenceText>%s</ProviderReferenceText><ExternalReference>%s</ExternalReference></Request></AutoCreate>'%(self.api_username, self.api_password, amount, phone_number, narrative, ref_text, ext_ref_text)
		return self.send_xml_request(xml_request)


	def is_registered(self, phone_number, network, narrative="Remit.ug"):
		"""
		* Check if a phonenumber is registered
		* @param string phone_number Phone number to pull Mobile Money from <br> [Format]: 256772123456
		* @param string network The network provider code 
		* 
		* @return xml The XML Request String to be sent to the Yo! Payments Server
		*
		* ------------------------------------------------------------------------------------------------------------------
		*
		"""
		'''
		we vary the external reference , this seems to solve the duplicate transaction error
		'''
		xml_request = '<?xml version="1.0" encoding="UTF-8"?><AutoCreate><Request><APIUsername>%s</APIUsername><APIPassword>%s</APIPassword><Method>acverifyaccountvalidity</Method><Account>%s</Account><AccountProviderCode>%s</AccountProviderCode></Request></AutoCreate>'%(self.api_username, self.api_password, phone_number, network)
		return self.send_xml_request(xml_request)




