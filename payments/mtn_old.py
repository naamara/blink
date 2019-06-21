'''mtn sdb'''
import remit.settings as settings
from datetime import datetime
import requests, base64
from BeautifulSoup import BeautifulSoup
from remit.tasks import send_sms, send_email
from remit.utils import debug, mailer
from xml.sax.saxutils import escape
from xml.sax.saxutils import quoteattr
import json
import xmltodict
import suds
import datetime
import time
#import logging
#logging.getLogger('suds.client').setLevel(logging.CRITICAL)
from suds.sax.element import Element
import logging
#logging.basicConfig(level=logging.INFO)
#logging.getLogger('suds.transport.http').setLevel(logging.DEBUG)
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)
from suds.sudsobject import asdict
#logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
#logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)


class Mtn():
	"""mtn mobile money functions"""


	def __init__(self):
		self.base_path = "file:%spayments/wsdl/" % settings.BASE_DIR
		self.OrderDateTime = unicode(datetime.datetime.now().isoformat()).partition('.')[0]+"Z"
		self.OpCoID = 'UG'
		self.SenderID = 'MTN'
		self.VendorCode='REMITUG'
		self.TypeCode='GSM'
		self.OrderDateTimestamp = int(time.time())

	def get_client(self, filename, url, headers=False):
		base_url = "%s%s" % (
			self.base_path,
			filename
			)
		import base64
		import hashlib
		Nonce = "gagdasgsagasdgsadgsadsda"
		Created = self.OrderDateTime
		digest = "%s%s%s"%(Nonce,Created,settings.MTN_SDP_PASS)
		digest =  hashlib.sha1(digest).digest()
		PasswordDigest = base64.encodestring(digest).replace('\n', '')
		if not headers:
			headers = {
			#'Host': '172.25.48.43:8312',
			#'X-RequestHeader': 'FA="256783370747"',
			'Accept-Encoding': 'gzip,deflate',
			'Accept': 'application/json',
			'Content-Type: application/json'
			'Authorization': 'WSSE realm="SDP", profile="UsernameToken"',
			'X-WSSE': 'UsernameToken Username="%s", PasswordDigest="%s",Nonce="%s",Created="%s"' % (
			#settings.MTN_SDP_USERNAME,
			settings.MTN_SDP_SERVICEID,
			PasswordDigest,
			Nonce,
			Created
			),
			}
		from suds.xsd.doctor import Import, ImportDoctor
		# Fix missing types with ImportDoctor
		schema_url = 'http://www.type-applications.com/character_set/'
		schema_import = Import(schema_url)
		schema_doctor = ImportDoctor(schema_import)
		client = suds.client.Client(base_url, headers=headers,  doctor=schema_doctor)
		list_of_methods = [method for method in client.wsdl.services[0].ports[0].methods]
                print "Available methods %s" % list_of_methods
	        #client.options.location = url 
		client.options.location = url
		print client
		return client

	def DepositMoney(self, amount, number, transactionid, ref_text=""):
		'''
		deposit Mobile Money into users phonenumber
		'''
		number = self.clean_number(number)
		url = 'http://172.25.48.43:8310/ThirdPartyServiceUMMImpl/UMMServiceService/DepositMobileMoney/v17'
		headers = {
			'spld': '%s' % settings.MTN_SDP_SERVICEID,
			'serviceId': '201',
			'Content-Type': 'text/xml; charset=utf-8',
			}
		import hashlib
		m = hashlib.md5()
		digest = "%s%s%s" % (settings.MTN_SDP_SERVICEID,settings.MTN_SDP_PASS,self.OrderDateTimestamp)
		m.update(digest)
                PasswordDigest = m.hexdigest()#.replace('\n', '')
		from suds.sax.attribute import Attribute
		client = self.get_client("DepositMobileMoney.wsdl", url, headers=headers)
		code = Element('spId').setText('%s' % settings.MTN_SDP_SERVICEID)
                pwd = Element('spPassword').setText('%s'%PasswordDigest)
		tsp = Element('timeStamp').setText('%s'%self.OrderDateTimestamp)
		reqsoapheader = Element('RequestSOAPHeader')
		reqsoapheader.insert(code)
		reqsoapheader.insert(pwd)
		reqsoapheader.insert(tsp)
		reqsoap_attribute = Attribute('xmlns', "http://www.huawei.com.cn/schema/common/v2_1")
   	        reqsoapheader.append(reqsoap_attribute) 
		client.set_options(soapheaders=reqsoapheader)  
		#CommonComponents = {}
		CommonComponents = [
		{
		"name": "ProcessingNumber",
		"value": transactionid
		},
		{
		"name": "serviceId",
		#"value": 'WEETULI.sp1'#settings.MTN_SDP_USERNAME
		#"value": 'remitug.sp1'
		'value': '%s' % settings.MTN_SDP_USERNAME
		},
		{
		"name": "SenderID",
		"value": 'MOM'
		},
		{
		"name": "PrefLang",
		"value": 121212121
		},
		{
		"name": "OpCoID",
		"value": '25601'#self.OpCoID
		},
		{
		"name": "CurrCode",
		"value": 'UGX'
		},
		{
		"name": "MSISDNNum",
		'value': '%s' % number
		},
		{
		"name": "Amount",
		"value": amount
		},
		{
		"name": "Narration",
		"value": "sdf"
		},
		{
		"name": "OrderDateTime",
		"value": self.OrderDateTimestamp,
		},
		]
		response = client.service.DepositMobileMoney(
			'201',#settings.MTN_SDP_SERVICEID,
			CommonComponents
			)
		data = {'status': '', 'statuscode': '', 'response': response}
		try:
			status = response[0].value
			print status


			if status == '01':
				data = {'status': 'Ok', 'statuscode': '0', 'response': response}

				try:
					momid = response[2].value
					data['transaction_response_id'] = momid
					print momid
				except Exception, e:
					print e
				return data

			elif status == '108':
				'''Deposit Transfer not processed: Insufficient funds'''
				self.stone_fucked_up()
			#for key,value in response:
			#	print "key: %s , value: %s" % (key,value)
			#return self.suds_to_json(response)
		except Exception, e:
			print e
		return data
		#print query_request

	def stone_fucked_up(self):
		print "we have Insufficient funds"

	def SendNotification(self):
		'''
		deposit Mobile Money into users phonenumber
		'''
		url = 'http://172.25.48.43:8310/SendNotification'
		client = self.get_client("SendNotification.wsdl", url)
		query_request = client.factory.create('SendNotification')
		print query_request
		try:
		   
		   response = client.service.SendNotification(
		   	'1111','adsadasdsad','adasdasd','asdasdasd','asdsadasdasd','asdasdasdsad','wwwwww')
		   #response.VendorCode = '333333'
		   print str(response)	
		except Exception, e:
		   print "Remit Error %s" % e
		   pass

	def clean_number(self, number):
		number = "%s" % number
		if number[0] == '0':
			return number[1:]
		return number

	def kyc_sms(self, number):
		number = "256%s" % self.clean_number(number)
		sms = "Y'ello. Please visit an MTN Service Centre with a valid ID to complete your SIM card validation immediately to be able to receive money from MTN International Remittance."
		if settings.SEND_KYC_SMS:
			return send_sms(number, {}, {}, sms)
		return True

	def momo_sms(self, number):
		number = "256%s" % self.clean_number(number)
		sms = "Y'ello. Please visit an MTN Service Centre with a valid ID to complete your mobile money registration immediately to be able to receive money from MTN International Remittance."
		if settings.SEND_KYC_SMS:
			return send_sms(number, {}, {}, sms)
		return True

	def kyc_email(self, number, email, request, transaction):
		# send email to sender
		template = settings.EMAIL_TEMPLATE_DIR + 'unregistered_recipient.html'
		c = {'number':number, 'transaction':transaction}
		return mailer(request, 'Unregistered Recipient', template, c, email)


	def CheckNumber(self, number="789999550", OperationType="ProfileDetails"):
		number = self.clean_number(number)
		import base64
		import hashlib
		result = 'Failed'
		Nonce = "%s" % self.OrderDateTimestamp 
		Created = self.OrderDateTime
		digest = "%s%s%s" % (Nonce, Created, settings.MTN_SDP_PASS)
		digest =  hashlib.sha1(digest).digest()
		PasswordDigest = base64.encodestring(digest).replace('\n', '')
		data = {
		"ProcessCustomerRequest": {
		"TypeCode": "GSM",
		"OperationType": OperationType,
		"VendorCode": "REMITUG",
		"CommonComponents": {
		"MSISDNNum": "%s" % number,
		"ProcessingNumber": "1230909",
		"OrderDateTime": "%s" % self.OrderDateTime,
		"OpCoID": "UG",
		"SenderID": "SDP"
		},
		"SpecificationGroup": [{
		"Narration": "CustomerDetails",
		"Specification": [{
		"Name": "LevelCode",
		"Value": "ServiceLevel"
		},
		{
		"Name": "ServiceID",
		"Value": "%s" % number,
		}]
		}]
		}
		}
		headers = {
		'Host': 'http://172.25.48.43:8312',
		'X-RequestHeader': 'FA="%s"' % number,
		'Accept-Encoding': 'gzip,deflate',
		'Accept': 'application/json',
		'Content-Type': 'application/json',
		'Authorization': 'WSSE realm="SDP", profile="UsernameToken"',
		'X-WSSE': 'UsernameToken Username="%s", PasswordDigest="%s",Nonce="%s",Created="%s"' % (
		settings.MTN_SDP_SERVICEID,
		PasswordDigest,
		Nonce,
		Created
		),
		}
		import requests
		try:
			url = 'http://172.25.48.43:8312/1/generic/processcustomer'
			r = requests.post(url, json=data, headers=headers)
			data = json.loads(r.text)
			print data
			if 'ProcessCustomerRequestResponse' in data:
				response =  data['ProcessCustomerRequestResponse']['SpecificationGroup']
				response = response[0]['Specification']
				registration_status = response[1]['Value']
				result = registration_status
		except Exception, e:
			print e
			pass
		print result
		return result


	def validateAcountHolder(self, number="256789945550"):
		import base64
		import hashlib
		import json
		import xmltodict
		if not number[:3] == '256':
			number = "256%s" % self.clean_number(number)
		Nonce = "gdhdgdhdgdhdhdgdh"
		Created = self.OrderDateTime
		digest = "%s%s%s"%(Nonce,Created,settings.MTN_SDP_PASS)
		digest =  hashlib.sha1(digest).digest()
		PasswordDigest = base64.encodestring(digest).replace('\n', '')
		headers = {
		'X-RequestHeader': 'request ServiceId=, TransId="1430215126132",FA="%s"' % number,
		'Msisdn': '%s' % number,
		'Content-Type': 'text/xml; charset=utf-8',
		'Authorization': 'WSSE realm="SDP", profile="UsernameToken"',
		'X-WSSE': 'UsernameToken Username="%s", PasswordDigest="%s",Nonce="%s",Created="%s"' % (
		settings.MTN_SDP_SERVICEID,
		PasswordDigest,
		Nonce,
		Created
		),
		}
		response = {'valid': False}
		xml = '<?xml version="1.0" encoding="utf-8"?><validateaccountholderrequest><accountholderid>ID:%s/MSISDN</accountholderid></validateaccountholderrequest>' % number
		url = 'http://172.25.48.43:8323/mom/mt/validateaccountholder'
		req = requests.Request('POST',url,headers=headers,data=xml)
		prepared = req.prepare()
		self.pretty_print_POST(prepared)
		s = requests.Session()
		r = s.send(prepared)
		print r.text
		try:
			response = json.dumps(xmltodict.parse('%s' % r.text))
			response =  json.loads(response)
			response = response['validateaccountholderresponse']
		except Exception, e:
			print e
			response['error'] = True
			pass
		return response


	def pretty_print_POST(self, req):
		"""
		At this point it is completely built and ready
		to be fired; it is "prepared".

		However pay attention at the formatting used in 
		this function because it is programmed to be pretty 
		printed and may differ from the actual request.
		"""
		print('{}\n{}\n{}\n\n{}'.format(
		'-----------START-----------',
		req.method + ' ' + req.url,
		'\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
		req.body,
		))

	def recursive_asdict(self, d):
	    """Convert Suds object into serializable format."""
	    out = {}
	    for k, v in asdict(d).iteritems():
	        if hasattr(v, '__keylist__'):
	            out[k] = recursive_asdict(v)
	        elif isinstance(v, list):
	            out[k] = []
	            for item in v:
	                if hasattr(item, '__keylist__'):
	                    out[k].append(recursive_asdict(item))
	                else:
	                    out[k].append(item)
	        else:
	            out[k] = v
	    return out

	def suds_to_json(self, data):
	    return json.dumps(self.recursive_asdict(data))

	def kyc_check(self, number):
		is_kyc = False
		try:
			response = self.CheckNumber(number)
			if response == 'RegisteredComplete':
				is_kyc = True
		except Exception, e:
			print e
			pass
		return is_kyc

	def momo_check(self, number):
		is_momo = False
		response = {}
		try:
			response = self.validateAcountHolder(number)
			if response['valid'] == 'true':
				is_momo = True
		except Exception, e:
			print e
			pass
		return is_momo, response






def test_api_call():
	mtn = Mtn()
	#mtn.DepositMoney()
	#mtn.CheckNumber()
	mtn.validateAcountHolder()
