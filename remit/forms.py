from django import forms
from remit.models import Transaction, Phonebook


class PayBillForm(forms.ModelForm):
    amount_sent = forms.CharField(label="Amount", required=True,)
    amount_received = forms.CharField(label="Amount", required=True,)
    referencenumber = forms.CharField(label="Account number", required=True,)
    billtype = forms.CharField(label="billtype", required=True,)
    utility_account_name = forms.CharField(label="Bill account name", required=False,)
    utility_account_type = forms.CharField(label="Bill account type", required=False,)
    receiver_number = forms.CharField(
        label="Customer Phonenumber", required=True,)

    class Meta:
        model = Transaction
        fields = ['billarea','billtype', 'amount_sent', 'receiver_number', 'receiver_fname', 'receiver_lname', 'user', 'amount_received', 'receiver_country_code', 'utility', 'referencenumber','utility_account_name','utility_account_type']



class QueryPayBillForm(forms.Form):
    billtype = forms.CharField(label="Bill type", required=True,)
    location = forms.CharField(label="location", required=False)
    referencenumber = forms.CharField(label="Account number", required=True,)


class RateUpdateForm(forms.Form):
	"""
	Form for updating rates
	"""


class sendMoneyForm(forms.ModelForm):
	"""
	Form for sending money
	"""
	phonenumber_ext = forms.TextInput(attrs=dict(maxlength=3)),
	class Meta:
		model = Transaction
		fields = ['amount_sent', 'receiver_number', 'receiver_fname', 'receiver_lname', 'user', 'mobile_reason', 'amount_received', 'receiver_country_code']


class AddToPhonebookForm(forms.ModelForm):
	"""
	Form for saving phonebook
	"""
	class Meta:
		model = Phonebook
		fields = ['user', 'number', 'firstname', 'lastname', 'ext', 'country_code']



from datetime import date, datetime
from calendar import monthrange

class CreditCardField(forms.IntegerField):
    @staticmethod
    def get_cc_type(number):
        """
        Gets credit card type given number. Based on values from Wikipedia page
        "Credit card number".
        http://en.wikipedia.org/w/index.php?title=Credit_card_number
        """
        number = str(number)
        #group checking by ascending length of number
        if len(number) == 13:
            if number[0] == "4":
                return "Visa"
        elif len(number) == 14:
            if number[:2] == "36":
                return "MasterCard"
        elif len(number) == 15:
            if number[:2] in ("34", "37"):
                return "American Express"
        elif len(number) == 16:
            if number[:4] == "6011":
                return "Discover"
            if number[:2] in ("51", "52", "53", "54", "55"):
                return "MasterCard"
            if number[0] == "4":
                return "Visa"
        return "Unknown"

    def clean(self, value):
        """Check if given CC number is valid and one of the
           card types we accept"""
        if not value:
        	raise forms.ValidationError("Please enter in a Visa, "+\
                "Master Card, or American Express credit card number.")
        value = value.replace(" ", "")
        if value and (len(value) < 13 or len(value) > 16):
            raise forms.ValidationError("Please enter in a valid "+\
                "credit card number.")
        elif self.get_cc_type(value) not in ("Visa", "MasterCard",
                                             "American Express"):
            raise forms.ValidationError("Please enter in a Visa, "+\
                "Master Card, or American Express credit card number.")
        return super(CreditCardField, self).clean(value)


class CCExpWidget(forms.MultiWidget):
    """ Widget containing two select boxes for selecting the month and year"""
    def decompress(self, value):
        return [value.month, value.year] if value else [None, None]

    def format_output(self, rendered_widgets):
        html = u' / '.join(rendered_widgets)
        return u'<span style="white-space: nowrap">%s</span>' % html


class CCExpField(forms.MultiValueField):
    EXP_MONTH = [(x, x) for x in xrange(1, 13)]
    EXP_YEAR = [(x, x) for x in xrange(date.today().year,
                                       date.today().year + 15)]
    default_error_messages = {
        'invalid_month': u'Enter a valid month.',
        'invalid_year': u'Enter a valid year.',
    }

    def __init__(self, *args, **kwargs):
        errors = self.default_error_messages.copy()
        if 'error_messages' in kwargs:
            errors.update(kwargs['error_messages'])
        fields = (
            forms.ChoiceField(choices=self.EXP_MONTH,
                error_messages={'invalid': errors['invalid_month']}),
            forms.ChoiceField(choices=self.EXP_YEAR,
                error_messages={'invalid': errors['invalid_year']}),
        )
        super(CCExpField, self).__init__(fields, *args, **kwargs)
        self.widget = CCExpWidget(widgets =
            [fields[0].widget, fields[1].widget])

    def clean(self, value):
        exp = super(CCExpField, self).clean(value)
        if date.today() > exp:
            raise forms.ValidationError(
            "The expiration date you entered is in the past.")
        return exp

    def compress(self, data_list):
        if data_list:
            if data_list[1] in forms.fields.EMPTY_VALUES:
                error = self.error_messages['invalid_year']
                raise forms.ValidationError(error)
            if data_list[0] in forms.fields.EMPTY_VALUES:
                error = self.error_messages['invalid_month']
                raise forms.ValidationError(error)
            year = int(data_list[1])
            month = int(data_list[0])
            # find last day of the month
            day = monthrange(year, month)[1]
            return date(year, month, day)
        return None


EXP_MONTH = [(x, x) for x in xrange(1, 13)]
EXP_YEAR = [(x, x) for x in xrange(date.today().year,
                                       date.today().year + 15)]

class doCCForm(forms.Form):
    cc_number = CreditCardField(required = True, label = "Card Number")
    cc_fname = forms.CharField(required = True, label = "Card Holder First Name",
        max_length = 60)
    cc_lname = forms.CharField(required = True, label = "Card Holder Last Name",
        max_length = 60)
    cc_ctry = forms.CharField(required = True, label = "Country")
    cc_cty = forms.CharField(required = True, label = "City")
    cc_phonnumber = forms.CharField(required = True, label = "Phonenumber")

    #cc_exp_	 = CCExpField(required = True, label = "Expiration")
    cc_exp_month = forms.IntegerField(required = True, label = "Expiration Month")
    cc_exp_year = forms.IntegerField(required = True, label = "Expiration Year")
    cc_cvc = forms.IntegerField(required = True, label = "CCV Number",
        max_value = 9999, widget = forms.TextInput(attrs={'size': '4'}))

    def __init__(self, *args, **kwargs):
        self.payment_data = kwargs.pop('payment_data', None)
        super(doCCForm, self).__init__(*args, **kwargs)
