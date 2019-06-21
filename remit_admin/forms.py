'''ModelForms for Admin'''
from django import forms
from remit.models import Rate, Phonebook, Transaction, Charge
from accounts.models import Profile
from remit_admin.models import EmailSupport
from django.contrib.auth.models import User
from accounts.models import Create_staff_User,AddInfo

class ChargesLimitsForm(forms.ModelForm):
    '''charges limits form'''
    class Meta(object):
        """docstring for Meta"""
        model=Charge
        #fields = '__all__'
        fields = ['forex_percentage', 'transfer_fee_percentage', 'transfer_maximum_usd',
        'transfer_minimum_usd','general_network_charge','mtn_charge','airtel_charge','safaricom_charge']
            
        

class RateUpdateForm(forms.ModelForm):

    """
    Form for updating rates
    """
    class Meta:
        model = Charge
        fields = ['to_usd', 'to_gbp', 'to_eur']
        #fields = ['usd_to_ugx', 'usd_to_kes','usd_to_kzs','gbp_to_ugx','transfer_limit_usd','transfer_minimum_usd','our_percentage','added','user','']


class TransactionUpdateForm(forms.ModelForm):

    """
    Form for updating transactions
    """
    class Meta:
        model = Transaction
        fields = ['receiver_country_code','receiver_number']


class ProfileUpdateForm(forms.ModelForm):

    """
    Form for updating user profile
    """
    class Meta:
        model = Profile
        fields = ['firstname', 'lastname', 'dob', 'id_number']



class ProfileAddForm(forms.ModelForm):

    """
    Form for migrating user profile
    """
    class Meta:
        model = Profile
        fields = ['user', 'country_code', 'phonenumber',
                  'account_verified', 'id_number',
                  'firstname', 'lastname', 'city',
                  'country', 'dob',
                  'userdetails_provided', 'id_verified', 'verified_by']


class PhonebookAddForm(forms.ModelForm):

    """
    Form for migrating user phonebook
    """
    class Meta:
        model = Phonebook
        fields = ['user',
                  'firstname',
                  'lastname',
                  'number',
                  'ext']


class TransactionAddForm(forms.ModelForm):

    """
    Form for migrating user phonebook
    """
    class Meta:
        model = Transaction
        fields = ['user',
                  'receiver_number',
                  'receiver_country_code',
                  'amount_sent',
                  'processed_on',
                  'is_processed',
                  'visa_success',
                  'exchange_rate',
                  'amount_received',
                  'started_on', ]


class CreateAdminUserForm(forms.ModelForm):

    """
    Form for migrating user phonebook
    """
    username = forms.CharField(required=True, max_length=255)
    email = forms.EmailField(required=True, max_length=255)
    category = forms.CharField(required=True, max_length=200)
    cat_name = forms.CharField(required=True, max_length=200)
    doct_name = forms.CharField(required=True, max_length=800)
    role = forms.CharField(required=True, max_length=200)
    password = forms.CharField(required=True, max_length=255)
    phone = forms.CharField(required=True, max_length=20)
    info = forms.CharField(required=True, max_length=900)
    password2 = forms.CharField(required=True, max_length=20)
    region = forms.CharField(required=True, max_length=80)
    districts = forms.CharField(required=True, max_length=90)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def clean(self):

        # check passwords
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password1 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return self.cleaned_data

    def clean_username(self):
        data = self.cleaned_data['username']
        if User.objects.filter(username=data).exists():
            raise forms.ValidationError('Username already taken.')
        return data

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email is already taken.')
        return data



class CreateHealthUserForm(forms.Form):

    """
    Form for migrating user phonebook
    """

    username = forms.CharField(required=True, max_length=255)
    email = forms.EmailField(required=True, max_length=255)
    category = forms.CharField(required=True, max_length=200)
    cat_name = forms.CharField(required=True, max_length=200)
    doct_name = forms.CharField(required=True, max_length=800)
    role = forms.CharField(required=True, max_length=200)
    password = forms.CharField(required=True, max_length=255)
    phone = forms.CharField(required=True, max_length=20)
    info = forms.CharField(required=True, max_length=900)
    password2 = forms.CharField(required=True, max_length=20)
    region = forms.CharField(required=True, max_length=80)
    districts = forms.CharField(required=True, max_length=90)


    def clean(self):

        # check passwords
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password1 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return self.cleaned_data


class AddHealthInfoForm(forms.Form):

    """
    Form for migrating user phonebook
    """

    title_health = forms.CharField(required=True, max_length=255)
    message = forms.CharField(widget=forms.Textarea(attrs={'cols': 20, 'rows': 7,'placeholder': 'Message'}))


class AddLawInfoForm(forms.Form):

    """
    Form for migrating user phonebook
    """

    sub = forms.CharField(required=True, max_length=255)
    msg = forms.CharField(widget=forms.Textarea(attrs={'cols': 20, 'rows': 7,'placeholder': 'Message'}))


class AddPubInfoForm(AddLawInfoForm):
    pass

class AddEducInfoForm(AddLawInfoForm):
    pass


class AddInfoForm(forms.ModelForm):
    """
    Form for migrating user phonebook
    """

    class Meta:
        model = AddInfo

        fields = ['info']
        




class EditAdminUserForm(forms.ModelForm):

    """
    Form for migrating user phonebook
    """

    password2 = forms.CharField(required=False, max_length=255)
    password = forms.CharField(required=False, max_length=255)
    rates = forms.CharField(required=True, max_length=1)
    transactions = forms.CharField(required=True, max_length=1)
    users = forms.CharField(required=True, max_length=1)
    reports = forms.CharField(required=True, max_length=200)
    email = forms.EmailField(required=True, max_length=255)
    network = forms.CharField(required=True, max_length=20)
    country = forms.CharField(required=True, max_length=20)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def clean(self):

        # check passwords
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords don't match")
        return self.cleaned_data

    def clean_username(self):
        data = self.cleaned_data['username']
        if not data == self.instance.username:
            raise forms.ValidationError('Invalid Stuff Username, Dont Change these Values')
        return data


    def clean_email(self):
        data = self.cleaned_data['email']
        if not data == self.instance.email:
            raise forms.ValidationError('Invalid Stuff Email, Dont Change these Values')
        return data



class ContactUserForm(forms.ModelForm):

    """
    Form for migrating user phonebook
    """
    class Meta:
        model = EmailSupport
        fields = ['user',
                  'msg',
                  'subject',
                  'support_staff',
                   ]


class transactionPhonenumberSearchForm(forms.Form):
    phonenumber = forms.CharField(required = True, label = "Phonenumber to search",
        max_length = 60)


