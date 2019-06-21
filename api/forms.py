'''forms for the django api'''
from django import forms
from remit.forms import CreditCardField


class CcForm(forms.Form):
	'''form that checks cc data'''
	cc_number = CreditCardField(required = True, label = "Card Number")
	cc_firstname = forms.CharField(required = True, label = "Card Holder First Name",
	max_length = 60)
	cc_lastname = forms.CharField(required = True, label = "Card Holder Last Name",
	max_length = 60)
	cc_country = forms.CharField(required = True, label = "Country")
	cc_city = forms.CharField(required = True, label = "City")
	cc_phonenumber = forms.CharField(required = True, label = "Phonenumber")

	#cc_exp_	 = CCExpField(required = True, label = "Expiration")
	cc_expiry_month = forms.IntegerField(required = True, label = "Expiration Month")
	cc_expiry_year = forms.IntegerField(required = True, label = "Expiration Year")
	cc_cvv = forms.IntegerField(required = True, label = "CCV Number",
	max_value = 9999,)
	amount = forms.IntegerField(required = True, label = "Amount to be charged")
	currency = forms.CharField(required = True, label = "User currency",
	max_length = 3)
	recipient_number = forms.IntegerField(required = True, label = "Recipient number")
	recipient_firstname = forms.CharField(required = True, label = "Recipient First Name",
	max_length = 60)
	recipient_lastname = forms.CharField(required = True, label = "Recipient Last Name",
	max_length = 60)
	recipient_message = forms.CharField(required = False, label = "Recipient Message",
	max_length = 200)
	#vendor is the client we are dealing with an hmac of username , pass and randomly selected vendor string 
	vendor = forms.CharField(required = True, label = "The Vendor we are dealing with",
	max_length = 60)