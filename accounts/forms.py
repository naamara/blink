'''account forms'''
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from accounts.models import Profile, UserActions, LoginInfo
from accounts.utils import change_email
from accounts.utils import migrate_user_login, get_user_model
from django.contrib.admin.models import LogEntry
import magic
try:
    from hashlib import sha1 as sha_constructor
except ImportError:
    from django.utils.hashcompat import sha_constructor


from remit.misc import COUNTRY_CODES

import random
from collections import OrderedDict
attrs_dict = {'required': 'required', 'class': 'span4'}



class SignupForm(forms.Form):

    """
    Form for creating a new user account.

    Validates that the requested username and e-mail is not already in use.
    Also requires the password to be entered twice.

    """
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_("Email"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                                                           render_value=False),
                                label=_("Create password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                                                           render_value=False),
                                label=_("Repeat password"))

    number = forms.IntegerField(
        widget=forms.TextInput(attrs=dict({'class': 'telnum', 'type': 'tel',
                                           'placeholder': "Mobile Number",
                                           "rel": "tooltip",
                                           "title": "No spaces or hyphenation, minus the country code",
                                           "required": "required"},
                                          maxlength=75)))

    ctry_code = forms.ChoiceField(
        widget=forms.Select(attrs=dict({'class': 'telnum_ext_select',
                                        'type': 'tel'})), choices=(COUNTRY_CODES))

    def clean_email(self):
        """ Validate that the e-mail address is unique. """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(
                _('This email is already in use. Please supply a different email.'))
        return self.cleaned_data['email']

    def clean(self):
        """
        Validates that the values entered into the two password fields match.
        Note that an error here will end up in ``non_field_errors()`` because
        it doesn't apply to a single field.

        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(
                    'The two password fields didn\'t match.')
        return self.cleaned_data

    def save(self):
        """ Creates a new user and account. Returns the newly created user. """

        '''custom username'''
        username = sha_constructor(str(random.random())).hexdigest()[:5]
        username, email, password = (username,
                                     self.cleaned_data['email'],
                                     self.cleaned_data['password1'])
        new_user = User.objects.create_user(
            username=username, email=email, password=password)
        new_user.save()
        return new_user






class SignupForm2(forms.Form):

    """
    Form for creating a new user account.

    Validates that the requested username and e-mail is not already in use.
    Also requires the password to be entered twice.

    """
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_("Email"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                                                           render_value=False),
                                label=_("Create password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict,
                                                           render_value=False),
                                label=_("Repeat password"))
    
    def clean_email(self):
        """ Validate that the e-mail address is unique. """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(
                _('This email is already in use. Please supply a different email.'))
        return self.cleaned_data['email']

    def clean(self):
        """
        Validates that the values entered into the two password fields match.
        Note that an error here will end up in ``non_field_errors()`` because
        it doesn't apply to a single field.

        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(
                    'The two password fields didn\'t match.')
        return self.cleaned_data

    def save(self):
        """ Creates a new user and account. Returns the newly created user. """

        '''custom username'''
        username = sha_constructor(str(random.random())).hexdigest()[:5]
        username, email, password = (username,
                                     self.cleaned_data['email'],
                                     self.cleaned_data['password1'])
        new_user = User.objects.create_user(
            username=username, email=email, password=password)
        new_user.save()
        return new_user


class AuthenticationForm(forms.Form):

    """
    A custom form where the identification can be a e-mail address or username.

    """
    identification = forms.EmailField(
        widget=forms.TextInput(attrs=dict(attrs_dict,
                                          maxlength=75)),
        label=_("Email"))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput(attrs=attrs_dict, render_value=False))

    def __init__(self, *args, **kwargs):
        """ A custom init because we need to change the label if no usernames is used """
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        # Dirty hack, somehow the label doesn't get translated without declaring
        # it again here.
        #self.fields['identification'] = forms.ValidationError(_(u"Email"),_(u"Please supply your email."))

    def clean(self):
        """
        Checks for the identification and password.

        If the combination can't be found will raise an invalid sign in error.

        """
        identification = self.cleaned_data.get('identification')
        password = self.cleaned_data.get('password')

        if identification and password:
            user = authenticate(username=identification, password=password)

            # if the user is not in this db we check if they are in the old
            if user is None:
                try:
                    data = {'email': identification, 'password': password}
                    user = migrate_user_login(data)
                except Exception, e:
                    pass

            if user is None:
                raise forms.ValidationError(
                    "Please enter a correct email and password. Note that both fields are case-sensitive.")
        return self.cleaned_data


"""
class UserDetailsForm(forms.ModelForm):

    #Form for saving user details on signup
    class Meta:
        model = Profile
        fields = ['firstname', 'lastname',
                  'address1', 'address2',
                  'dob', 'country', 'city', 'id_number']

"""


class UserDetailsForm(forms.ModelForm):

    """Form for saving user details on signup"""
    class Meta:
        model = Profile

        fields = ['firstname', 'lastname',
                  'address1', 'address2',
                  'dob', 'country', 'city', 'id_number']


class EditProfileForm(forms.ModelForm):

    """Form for saving user details on signup"""
    class Meta:
        model = Profile
        fields = ['firstname', 'lastname',
                  'address1', 'address2',
                  'dob', 'country', 'city', 'id_number']


class AccessRestrictedForm(forms.ModelForm):

    """Form for saving user details on signup"""
    access_restricted = forms.IntegerField(widget=forms.TextInput())

    class Meta:
        model = User
        fields = ['password']


class VerifyPhoneForm(forms.Form):
    phone_num = forms.IntegerField(
        widget=forms.TextInput(attrs=dict({'class': 'telnum', 'type': 'tel',
                                           'placeholder': "Mobile Number",
                                           "rel": "tooltip",
                                           "title": "No spaces or hyphenation, minus the country code",
                                           "required": "required"},
                                          maxlength=75)))
    phone_ext = forms.ChoiceField(
        widget=forms.Select(attrs=dict({'class': 'telnum_ext_select',
                                        'type': 'tel'})), choices=(COUNTRY_CODES))


class PassportUploadForm(forms.Form):

    """Image upload form."""
    #passport = forms.ImageField()
    passport = forms.FileField()
    firstname = forms.TextInput()
    lastname = forms.TextInput()
    id_number = forms.TextInput()

    class Meta:
        model = Profile
        fields = ['firstname', 'lastname', 'id_number']

    def clean_passport(self):
        _file = self.cleaned_data.get("passport", False)
        filetype = magic.from_buffer(_file.read())
        filetype = filetype.lower()
        exts = ['png', 'jpeg', 'jpg', 'pdf']
        for ext in exts:
            print ext
            if ext in filetype:
                return _file
        raise forms.ValidationError(
            "File is not valid type , please privode image or pdf.")


class PassportUploadForm_jumio(forms.Form):

    """Image upload form."""
    """
    passport = forms.ImageField()
    firstname = forms.TextInput()
    lastname = forms.TextInput()
    id_number = forms.TextInput()
    """
    id_scanned = forms.BooleanField()

    class Meta:
        model = Profile
        #fields = ['firstname', 'lastname', 'id_number']
        fields = ['id_scanned']


class RecoverPasswordForm(forms.Form):

    """Image upload form."""
    id_email = forms.EmailField()


class landingSendForm(forms.Form):

    """landing page send form."""
    mobile_number = forms.CharField(required=False)
    countrycode = forms.IntegerField()
    sendamount = forms.IntegerField()




class SetPasswordForm(forms.Form):

    """
    A form that lets a user change set his/her password without entering the
    old password
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    new_password1 = forms.CharField(label=_("New password"),
                                    widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("New password confirmation"),
                                    widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user


class PasswordChangeForm(SetPasswordForm):

    """
    A form that lets a user change his/her password by entering
    their old password.
    """
    error_messages = dict(SetPasswordForm.error_messages, **{
        'password_incorrect': _("Your old password was entered incorrectly. "
                                "Please enter it again."),
    })
    old_password = forms.CharField(label=_("Old password"),
                                   widget=forms.PasswordInput)

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password

PasswordChangeForm.base_fields = OrderedDict(
    (k, PasswordChangeForm.base_fields[k])
    for k in ['old_password', 'new_password1', 'new_password2']
)


class UpdatePhonenumberForm(forms.ModelForm):

    """Form for saving user details on signup"""
    class Meta:
        model = Profile
        fields = ['country_code', 'phonenumber']


class UpdateAvatarForm(forms.Form):

    '''update user avatar'''
    avatar = forms.ImageField()


class UpdateEmailForm(forms.Form):

    '''update user email'''
    email = forms.EmailField(required=True)

    def __init__(self, user, *args, **kwargs):
        """
        The current ``user`` is needed for initialisation of this form so
        that we can check if the email address is still free and not always
        returning ``True`` for this query because it's the users own e-mail
        address.

        """
        super(UpdateEmailForm, self).__init__(*args, **kwargs)
        if not isinstance(user, get_user_model()):
            raise TypeError, "user must be an instance of %s" % get_user_model().__name__
        else:
            self.user = user

    def clean_email(self):
        """ Validate that the email is not already registered with another user """
        if self.cleaned_data['email'].lower() == self.user.email:
            raise forms.ValidationError(
                _(u'You\'re already known under this email.'))
        if get_user_model().objects.filter(email__iexact=self.cleaned_data['email']).exclude(email__iexact=self.user.email):
            raise forms.ValidationError(
                _(u'This email is already in use. Please supply a different email.'))
        return self.cleaned_data['email']

    def save(self):
        '''return accounts.change_email which returns an email confirmation key'''
        return change_email(self.user.username, self.cleaned_data['email'])


class UserActionsForm(forms.ModelForm):

    """Form for saving user details on signup"""
    class Meta:
        model = UserActions
        fields = ['session', 'log_entry', 'user']


class LoginInfoForm(forms.ModelForm):

    """Form for saving user details on login"""
    class Meta:
        model = LoginInfo
        fields = ['user_agent', 'remote_addr', 'user']


class LogEntryForm(forms.ModelForm):

    """Form for saving user details on signup"""
    class Meta:
        model = LogEntry
        fields = ['user', 'content_type', 'object_id',
                  'object_repr', 'action_flag', 'change_message']
