from django import forms
#http://127.0.0.1/newremit/newremit/payments/do_cc/2882399945/?txncd=1860164115&qwh=&afd=&poi=&uyt=&ifd=&agt=&id=&status=aei7p7yrx4ae34&ivm=&mc=&p1=&p2=&p3=&p4=&msisdn_id=Madra%20David&msisdn_idnum=


class CheckIpayForm(forms.Form):
	'''check ipay form'''
	txncd = forms.CharField(required = True, max_length = 200)
	status = forms.CharField(required = True, max_length = 200)
	msisdn_id = forms.CharField(required = True, max_length = 200)
