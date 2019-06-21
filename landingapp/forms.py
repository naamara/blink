'''landing app forms'''
from django import forms
from django.utils.translation import ugettext_lazy as _
from remit.misc import COUNTRY_CODES

attrs_dict_required = {'required': 'required', 'class': 'span4'}
attrs_dict = {'class': 'span4'}

class ContactUsForm(forms.Form):

    """
    Contat Us Form
    """

    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict_required,
                                                               maxlength=75)),
                             label=_("Email"))

    names = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                              maxlength=75)),
                            label=_("Names"))

    phonenumber = forms.RegexField(required=False,regex=r'^\+?1?\d{9,15}$',
                                   error_message=("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."))


    msg = forms.CharField(widget=forms.TextInput(attrs=dict(attrs_dict_required,
                                                                maxlength=256)),
                              label=_("Message"))



