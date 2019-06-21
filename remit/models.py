from django.db import models
from django.contrib.sites.models import Site
# Create your models here.
from django.contrib.auth.models import User
from datetime import datetime
from remit.money import Money
from decimal import Decimal
from remit.utils import get_mobile_network_code, country_extensions, debug
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import intcomma
from remit.utils import NETWORK_CHOICES
import time
from django.core.exceptions import ValidationError
from remit.managers import MobileMoneyTransactionManager, BillPaymentTransactionManager


class Country(models.Model):
    code = models.CharField(blank=False, max_length=4, unique=True)
    name = models.CharField(blank=False, max_length=40)
    currency = models.CharField(blank=False, max_length=4, unique=True)
    user = models.ForeignKey(User)
    added = models.DateTimeField(default=datetime.now, blank=True)
    dailing_code = models.CharField(blank=False, max_length=5, default=256)

    @models.permalink
    def admin_charges_limits_url(self):
        return ('admin:admin_charges_limits', (str(self.code),),)

    @models.permalink
    def admin_rates_limits_url(self):
        return ('admin:admin_rates', (str(self.code),),)

    @property
    def rates(self):
        charge = Charge.objects.get(country=self.pk)
        return charge

    @property
    def pending_transaction_count(self):
        count = len(Transaction.momo.filter(to_country=self.pk).pending())
        return count

    @property
    def pending_transaction_amount(self):
        from django.db.models import Sum
        count = Transaction.momo.filter(
            to_country=self.pk).pending().aggregate(Sum('amount_received'))
        count = count['amount_received__sum']
        return count

    @property
    def successful_transaction_amount(self):
        from django.db.models import Sum
        count = Transaction.momo.filter(
            to_country=self.pk).successful().aggregate(Sum('amount_received'))
        count = count['amount_received__sum']
        return count


class Wallet(models.Model):
    user = models.ForeignKey(User, unique=True)
    balance = models.DecimalField(
        default=0.0, decimal_places=2, max_digits=10)
    currency = models.CharField(
        max_length=4,
        default='USD',
        blank=True,
    )
    credit = models.DecimalField(
        default=0.0, decimal_places=2, max_digits=10)
    debit = models.DecimalField(
        default=0.0, decimal_places=2, max_digits=10)
    added = models.DateTimeField(default=timezone.now)
    modified_by = models.ForeignKey(
        User,
        related_name='modified_by',
        blank=True,
        null=True
    )
    modified = models.DateTimeField(
        default=timezone.now,
        blank=True
    )

    @property
    def current_balance(self):
        return "%s" % self.balance

    @property
    def transactions(self):
        from remit.models import WalletTransaction
        return WalletTransaction.objects.filter(
            wallet=self
        ).order_by('-id')

    def save(self, *args, **kwargs):
        '''Auto Save Wallet'''
        add = self.pk
        if add:
            if not self.modified_by:
                errors = {}
                errors.setdefault('modified_by',
                                  []).append(u'You have to specify who is modifying this transaction')
                raise ValidationError(errors)
            else:
                if float(self.debit) > float(self.balance):
                    errors = {}
                    errors.setdefault('balance',
                                      []).append(u'You have insufficient balance')
                    raise ValidationError(errors)
                else:
                    """
                    credit = float(self.credit)
                    debit = float(self.debit)
                    balance = float(self.balance)
                    balance = balance + credit
                    balance = balance - debit
                    self.balance = float(balance)
                    self.modified = timezone.now()
                    """
        balance = self.compute_balance
        self.balance = balance
        super(Wallet, self).save(*args, **kwargs)

    @property
    def compute_balance(self):
        balance = 0.0
        admin = User.objects.get(pk=1)
        self.modified_by = admin
        transactions = self.transactions
        for transaction in transactions:
            amount = transaction.amount
            if amount > 0:
                amount = float(amount)
                if transaction.is_debit:
                    balance = balance - amount
                else:
                    balance = balance + amount
        balance = float(balance)
        return balance

    """

    @property
    def current_balance(self):
        obj = Wallet.objects.filter(user=self.user,
                                    currency=self.currency
                                    ).order_by('-id')[0]
        print "balance %s" % obj
        return float(obj.balance)

    @property
    def initial_balance(self):
        obj = Wallet.objects.filter(user=self.user,
                                    currency=self.currency
                                    ).order_by('id')[0]
        return float(obj.balance)
    """


class Charge(models.Model):
    '''currency and exchange rates for each country'''
    country = models.ForeignKey(Country, null=True, blank=True)
    forex_percentage = models.DecimalField(
        default=4.50, decimal_places=2, max_digits=10)
    transfer_fee_percentage = models.DecimalField(
        default=4.50, decimal_places=2, max_digits=10)
    transfer_maximum_usd = models.DecimalField(
        default=500.00, decimal_places=2, max_digits=10)
    transfer_minimum_usd = models.DecimalField(
        default=100.00, decimal_places=2, max_digits=10)

    bill_minimum_ugx = models.DecimalField(
        default=5000.00, decimal_places=2, max_digits=10)
    mtn_charge = models.DecimalField(
        default=60.00, decimal_places=2, max_digits=10)
    airtel_charge = models.DecimalField(
        default=60.00, decimal_places=2, max_digits=10)
    orange_charge = models.DecimalField(
        default=60.00, decimal_places=2, max_digits=10)
    tigo_charge = models.DecimalField(
        default=60.00, decimal_places=2, max_digits=10)
    safaricom_charge = models.DecimalField(
        default=60.00, decimal_places=2, max_digits=10)
    vodafone_charge = models.DecimalField(
        default=60.00, decimal_places=2, max_digits=10)
    general_network_charge = models.DecimalField(
        default=60.00, decimal_places=2, max_digits=10)
    user = models.ForeignKey(User)
    added = models.DateTimeField(default=datetime.now, blank=True)
    to_usd = models.DecimalField(
        default=2640.00, decimal_places=2, max_digits=10)
    to_gbp = models.DecimalField(
        default=3974.00, decimal_places=2, max_digits=10)
    to_eur = models.DecimalField(
        default=3256.00, decimal_places=2, max_digits=10)

    @property
    def last_update(self):
        epoch = int(time.mktime(self.added.timetuple()) * 1000)
        return epoch

    @property
    def currency(self):
        '''currency'''
        return str(self.country.currency)

    @property
    def hashid(self):
        '''
        invoice number
        '''
        return str(self.pk ^ 0xABCDEFAB)

    def get_default_rate(self, to_curr):
        '''return default rate , defaults to usd-ugx'''
        curr = 2500.00
        to_curr = to_curr.lower()
        if to_curr == 'usd':
            curr = self.to_usd
        if to_curr == 'gbp':
            curr = self.to_gbp
        if to_curr == 'eur':
            curr = self.to_eur
        return curr

    @property
    def extra_fees(self):
        '''extra network fees'''
        extra_fees = {}
        exts = country_extensions(self.country.code)
        this_charge = 0
        for key, value in exts.iteritems():
            if key == 'airtel':
                this_charge = self.airtel_charge
            elif key == 'safaricom':
                this_charge = self.safaricom_charge
            elif key == 'mtn':
                this_charge = self.mtn_charge
            elif key == 'tigo':
                this_charge = self.tigo_charge
            for x in value:
                extra_fees.update({x: '%s' % this_charge})
        return extra_fees

    def save(self, *args, **kwargs):
         # check if the charge already exists
        if not self.pk:
            if not Charge.objects.filter(country=self.country).exists():
                # continue with save, if necessary:
                super(Charge, self).save(*args, **kwargs)
            else:
                return
        else:
            super(Charge, self).save(*args, **kwargs)


class Rate(models.Model):

    '''Rates and Transaction limits'''
    from accounts.models import Profile

    class Meta:
        permissions = (
            ('view_rate', 'View Rates'),
            ('edit_rate', 'Edit Rates'),
        )

    '''fetch rates and store them'''
    site = models.OneToOneField(Site, default=1)
    usd_to_rwf = models.DecimalField(
        default=688.00, decimal_places=2, max_digits=10)
    gbp_to_rwf = models.DecimalField(
        default=1114.76, decimal_places=2, max_digits=10)
    usd_to_ugx = models.DecimalField(
        default=2640.00, decimal_places=2, max_digits=10)
    usd_to_kes = models.DecimalField(
        default=85.63, decimal_places=2, max_digits=10)
    usd_to_tzs = models.DecimalField(
        default=1623.00, decimal_places=2, max_digits=10)
    gbp_to_ugx = models.DecimalField(
        default=3974.19, decimal_places=2, max_digits=10)
    gpb_to_kes = models.DecimalField(
        default=129.47, decimal_places=2, max_digits=10)
    gpb_to_tzs = models.DecimalField(
        default=2453.00, decimal_places=2, max_digits=10)
    transfer_limit_usd = models.DecimalField(
        default=500.00, decimal_places=2, max_digits=10)
    transfer_minimum_usd = models.DecimalField(
        default=100.00, decimal_places=2, max_digits=10)
    bill_transfer_minimum_ugx = models.DecimalField(
        default=5000.00, decimal_places=2, max_digits=10)
    our_percentage = models.DecimalField(
        default=4.50, decimal_places=2, max_digits=10)
    percentage_from_forex = models.DecimalField(
        default=4.50, decimal_places=2, max_digits=10)
    user = models.ForeignKey(User)
    added = models.DateTimeField(default=datetime.now, blank=True)

    def get_rate(self, amount, rate=usd_to_ugx):
        return amount * self[rate]

    def currency_to_usd(self):
        'return the default currency amount in ugx'
        return self.usd_to_ugx

    def currency_transfer_maximum(self):
        'return the default currency amount transfer limit defaults to usd'
        return self.transfer_limit_usd

    def currency_transfer_minimum(self):
        'return the default currency amount transfer limit defaults to usd'
        return self.transfer_minimum_usd

    def remit_charge(self):
        'return the remit chagre defaults to our percentage'
        return self.our_percentage

    def kenyan_fees(self):
        '''temp value for kenyan fees'''
        # return 60
        return 0

    def get_default_rate(self, from_curr, to_curr):
        '''return default rate , defaults to usd-ugx'''
        curr = 2500.00
        from_curr = from_curr.lower()
        to_curr = to_curr.lower()
        if from_curr == 'usd':
            if to_curr == 'ugx':
                curr = self.usd_to_ugx
            if to_curr == 'tzs':
                curr = self.usd_to_tzs
            if to_curr == 'kes':
                curr = self.usd_to_kes
        return curr

    def last_modified_by(self):
        return self.user.username

    @property
    def airtel_charge(self):
        return 300

    @property
    def mtn_charge(self):
        '''temp value'''
        return 390
        # return 0


def current_percentage():
    '''current website percentage , backwards compatability , using Charge now'''
    return False


def current_rate():
    '''current rate , backwards compatability , using charge now'''
    return False


class Transaction(models.Model):

    '''remit Transactions'''
    from accounts.models import Profile as Profile

    class Meta:
        permissions = (
            ('view_transaction', 'View Transactions'),
            ('edit_transaction', 'Edit Transactions'),
            ('view_reports', 'View Reports'),
        )

    from_wallet = models.ForeignKey(
        Wallet,
        blank=True,
        null=True,
        related_name='Wallet')
    user = models.ForeignKey(User, related_name="owner")
    # rate defaults to current site rate
    exchange_rate = models.DecimalField(
        default=0.0, decimal_places=2, max_digits=10)
    currency_sent = models.CharField(default='UGX', max_length=3)
    currency_received = models.CharField(default='USD', max_length=3)
    amount_sent = models.DecimalField(
        null=False, blank=False, decimal_places=2, max_digits=10)
    amount_received = models.DecimalField(
        null=False, blank=False, decimal_places=2, max_digits=10)
    receiver_number = models.CharField(blank=False, max_length=130)
    receiver_country_code = models.CharField(default='256', max_length=3)
    receiver_fname = models.CharField(
        blank=True, max_length=30, default=False)
    receiver_lname = models.CharField(
        blank=True, max_length=30, default=False)
    started_on = models.DateTimeField(blank=False, default=timezone.now)
    added = models.DateTimeField(default=timezone.now)

    our_charge = models.DecimalField(
        default=0.0, decimal_places=2, max_digits=100)
    our_percentage = models.DecimalField(
        default=current_percentage, decimal_places=2, max_digits=10)
    total_charge = models.DecimalField(
        default=0.0, decimal_places=2, max_digits=10)
    other_fees = models.DecimalField(
        default=0.0, decimal_places=2, max_digits=10)

    visa_response_time = models.DateTimeField(null=True, blank=True)
    visa_response_code = models.CharField(
        blank=True, max_length=30, default=False)
    visa_response_metadata = models.TextField(blank=True, default=False)
    visa_success = models.BooleanField(default=False)
    visa_processed = models.BooleanField(default=False)

    mobile_response_time = models.DateTimeField(null=True, blank=True)
    mobile_response_code = models.CharField(
        blank=True, max_length=30, default=False)
    mobile_response_metadata = models.TextField(blank=True, default=False)
    mobile_reason = models.CharField(blank=True, max_length=220, default=False)

    is_processed = models.BooleanField(default=False)
    marked_as_processed = models.BooleanField(default=False)
    processed_on = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        User, null=True, blank=True, related_name="admin_processed")
    updated_by = models.ForeignKey(
        User, null=True, blank=True, related_name="admin_update_by")
    to_country = models.ForeignKey(
        Country, related_name="target_country", null=True, blank=True)
    mobile_network_code = models.CharField(
        blank=True, max_length=100, choices=NETWORK_CHOICES, default=False)
    sender_country = models.CharField(blank=True, max_length=30)
    utility = models.BooleanField(default=False)
    wallet = models.BooleanField(default=False)
    referencenumber = models.CharField(
        blank=True, default=False, max_length=230
    )
    billtype = models.CharField(blank=True, default=False, max_length=230)
    billarea = models.CharField(blank=True, default=False, max_length=230)
    is_canceled = models.BooleanField(default=False)
    canceled_reason = models.CharField(
        blank=True, default=False, max_length=230)
    utility_account_name = models.CharField(
        blank=True, default=False, max_length=230)
    utility_account_type = models.CharField(
        blank=True, default=False, max_length=230)
    utility_receipt_id = models.CharField(
        blank=True, default=False, max_length=230)
    utility_pegpay_id = models.CharField(
        blank=True, default='0', max_length=230)
    location = models.CharField(blank=True, default=False, max_length=600)
    canceled_by = models.ForeignKey(
        User, null=True, blank=True, related_name="admin_canceled")
    canceled_on = models.DateTimeField(null=True, blank=True)
    momo = MobileMoneyTransactionManager()
    billpayments = BillPaymentTransactionManager()
    objects = models.Manager()

    @property
    def last_pk(self):
        t = Transaction.objects.all().order_by('-id')[:1][0]
        return t.pk

    def get_network_transactionid(self):
        return "%s" % self.mobile_response_code

    def get_mobile_network(self):
        '''retuns mobile mobile'''
        number = '%s' % self.receiver_number
        return get_mobile_network_code(number)

    def revenue_share(self):
        from remit.settings import REVENUE_SHARE
        shs = 0
        if self.is_processed:
            try:
                percent = REVENUE_SHARE
                whole = float(self.amount_received)
                shs = (percent * whole) / 100.0
                shs = float(shs)
            except Exception, e:
                print e
        return shs

    @property
    def successful(self):
        '''
        filter successful Transactions
        '''
        result = False
        if self.visa_success and self.is_processed and self.amount_sent:
            result = True
        return result

    @property
    def hashid(self):
        '''
        invoice number
        '''
        return str(self.pk ^ 0xABCDEFAB)

    def get_invoice(self):
        '''
        invoice number
        '''
        return str(self.pk ^ 0xABCDEFAB)

    def get_sender_profile(self):
        from accounts.models import Profile
        '''
        sender profile
        '''
        return Profile.objects.get(user=self.user.pk)

    @models.permalink
    def admin_resend_email_url(self):
        return ('admin:resend_transaction_email', ({self.get_invoice()}), {})

    def get_order_id(self):
        '''
        invoice number
        '''
        return str(self.pk ^ 0xABCDEFAB)

    def recipient_number(self):
        '''
        number of person receiving the funds
        '''
        number = '%s%s' % (self.receiver_country_code, self.receiver_number)
        try:
            return str(number)
        except Exception, e:
            print "%s pk %s" % (e, self.pk)
        return number

    def paybill_recipient_number(self):
        '''
        number of person receiving the funds
        '''
        number = '%s%s' % (self.receiver_country_code, self.receiver_number)
        return str(number)

    
    @property
    def actual_amount_received(self):
        '''get actual amount sent'''
        ugx_amount = self.amount_received
        try:
            if self.other_fees:
                other_fees = float(self.other_fees)
                amount_received = float(ugx_amount)
                ugx_amount = amount_received - other_fees
        except Exception, e:
            print e
        try:
            ugx_amount = round(ugx_amount, 2)
        except Exception, e:
            print e
        return ugx_amount




    @property
    def other_fees_local(self):
        '''get other fees charged'''
        return self.other_fees

    @models.permalink
    def admin_url(self):
        '''return admin url link'''
        # print self.uid
        return ('admin:admin_transaction', ({self.get_invoice()}), {})

    @models.permalink
    def get_receipt_url(self):
        '''return admin url link'''
        # print self.uid
        return ('admin:transaction_receipt', ({self.get_invoice()}), {})

    @property
    def actual_initiation_date(self):
        from pytz import timezone
        try:
            return self.started_on.astimezone(timezone('Africa/Nairobi')).strftime("%d-%m-%Y %I:%M %p")
        except Exception, e:
            pass

    @property
    def actual_status(self):
        status = 'Failed'
        if self.is_processed:
            status = 'Processed'
        elif self.visa_success == True and self.is_processed == False and self.amount_sent is not None:
            status = 'Pending'
        return status

    @property
    def actual_delivery_date(self):
        from pytz import timezone
        try:
            return self.processed_on.astimezone(timezone('Africa/Nairobi')).strftime("%d-%m-%Y %I:%M %p")
        except Exception, e:
            pass

    def is_pending(self):
        pending = False
        if self.visa_success == True and self.is_processed == False and self.amount_sent is not None:
            pending = True
        return pending

    def processed_by_profile(self):
        from accounts.models import Profile
        profile = False
        try:
            profile = Profile.objects.get(user=self.processed_by.pk)
        except Exception, e:
            pass
        return profile

    def visa_response_data(self):
        from payments.payment import RESPONSE_CODES
        data = self.visa_response_code
        if data == RESPONSE_CODES['SUCCESS'] or self.visa_success:
            data = "Card Charged Successfully"
        else:
            data = "Failure Charging Card"

        if not data or data == 'False':
            data = 'N/A'
        return data

    def mobile_response_data(self):
        data = False
        data = self.mobile_response_metadata
        try:
            if 'statusmessage' in data:
                data = data['statusmessage']
        except Exception, e:
            pass
        if not data or data == 'False':
            data = 'N/A'
        return data

    def recipient_names(self):
        '''
        name of person receiving the funds
        '''
        name = '%s %s' % (self.receiver_fname, self.receiver_lname)
        return str(name)

    def sender_number(self):
        '''
        number of person sending the funds
        '''
        from accounts.models import Profile
        profile = Profile.objects.get(user=self.user)
        return "%s" % profile.get_phonenumber()

    def sender_names(self):
        '''
        number of person sending the funds
        '''
        from accounts.models import Profile
        profile = Profile.objects.get(user=self.user.pk)
        return "%s" % profile.get_names()

    def sender_reason(self):
        '''
        mobile money reason
        '''
        #from remit.settings import BASE_URL
        mobile_reason = self.mobile_reason
        if not mobile_reason or mobile_reason == 'False':
            #mobile_reason = "Mobile Money from %s via %s" % (self.sender_names(), BASE_URL)
            mobile_reason = "Mobile Money from %s" % self.sender_names()
        return mobile_reason

    def recipient_country(self):
        countries = {'256': 'UGANDA', '254': 'KENYA',
                     '255': 'TANZANIA', '250': 'RWANDA'}
        country = "UGANDA"
        try:
            country = str(countries[str(self.receiver_country_code)])
        except Exception, e:
            print e
        return country

    def display_amount_received(self):
        dollars = self.actual_amount_received
        currency = 'UGX'
        try:
            dollars = float(round(dollars, 2))
            currency = self.to_country.currency
        except Exception, e:
            pass
        return "%s %s" % (currency, intcomma(int(dollars)))


    def display_exchange_rate(self, amount=1):
        '''get the rate'''
        rate = Site.objects.get_current().rate
        code = int(self.receiver_country_code)
        dollars = rate.usd_to_ugx
        if code == 254:
            dollars = rate.usd_to_kes
        try:
            dollars = round(int(dollars), 0)
        except Exception, e:
            pass
        return "USD %s = %s %s" % (amount, self.to_country.currency, intcomma(int(dollars)))

    def get_extra_fees(self, number, rate):
        # other charges
        other_fees = False
        try:
            number = str(number)
            ext = number[:2]
            other_fees = rate.extra_fees[ext]
            other_fees = Decimal(str(other_fees))
        except Exception, e:
            debug(e, 'Error getting other fees', 'Transaction')
        return other_fees

    @property
    def get_our_charge(self):
        profile = self.get_sender_profile()
        rate = profile.current_rate()
        amount_sent = self.amount_sent
        our_charge = (rate.transfer_fee_percentage / 100) * amount_sent
        our_charge = float(str(our_charge))
        our_charge = Decimal(str(our_charge))
        return our_charge

    @property
    def get_total_charge(self):
        our_charge = self.get_our_charge
        total_charge = self.amount_sent
        total_charge = Decimal(str(total_charge)) + Decimal(str(our_charge))
        return total_charge

    def save(self, *args, **kwargs):
        add = not self.pk
        if add:

            # get Charge object
            profile = self.get_sender_profile()
            rate = profile.current_rate()

            try:
                self.amount_sent = Decimal(str(self.amount_sent))
            except Exception, e:
                pass

            # current exchange rate
            self.exchange_rate = rate.to_usd

            amount_sent = self.amount_sent

            # our charge
            """
            our_charge = rate.transfer_fee_percentage % amount_sent
            self.our_charge = Decimal(str(our_charge))

            # total charge
            total_charge = our_charge + amount_sent
            self.total_charge = Decimal(str(total_charge))
            """
            try:
                self.our_charge = self.get_our_charge
                self.total_charge = self.get_total_charge
            except Exception, e:
                print e

            self.to_country = rate.country

            # add the network
            number = '%s' % self.receiver_number
            self.mobile_network_code = get_mobile_network_code(number)

            r_amount = amount_sent * self.exchange_rate
            self.amount_received = r_amount

            self.other_fees = self.get_extra_fees(number, rate)

            if profile.country:
                self.sender_country = profile.country
            else:
                self.sender_country = 'UGANDA'
            # create() uses this, which causes error.
            kwargs['force_insert'] = False

            # Fast forward Pk Values
            try:
                from remit.settings import FORCE_TRANSACTION_ID
                if FORCE_TRANSACTION_ID:
                    self.pk = self.last_pk + 1
                    super(Transaction, self).save(*args, **kwargs)
            except Exception, e:
                print "Failed Forcing ID %s" % e
        super(Transaction, self).save(*args, **kwargs)
        return self


class Phonebook(models.Model):
    user = models.ForeignKey(User)
    ext = models.IntegerField(blank=False)
    number = models.IntegerField(blank=False)
    country_code = models.CharField(default='256', max_length=3)
    firstname = models.TextField(blank=False)
    lastname = models.TextField(blank=True, default=False)
    added = models.DateTimeField(blank=True, default=datetime.now)
    utility = models.BooleanField(default=False)

    def phonenumber(self):
        number = "%s%s" % (self.ext, self.number)
        return str(number)

    def phonenumber_with_countrycode(self):
        number = "%s%s%s" % (self.country_code, self.ext, self.number)
        return str(number)

    class Meta:
        unique_together = [
            "ext", "number", "firstname", "lastname", "country_code", "user"]


class WalletTransaction(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        related_name="transaction"
    )
    wallet = models.ForeignKey(
        Wallet,
        related_name="wallet"
    )
    added = models.DateTimeField(blank=True, default=timezone.now)
    modified = models.DateTimeField(blank=True, default=timezone.now)
    is_debit = models.BooleanField(default=True)
    amount = models.DecimalField(
        default=0.0, decimal_places=2, max_digits=10)
    current_balance = models.DecimalField(
        default=0.0, decimal_places=2, max_digits=10)
    added_by = models.ForeignKey(
        User,
        related_name="added_by_who"
    )
    modified_by = models.ForeignKey(
        User,
        related_name="modified_by_who",
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        '''make sure the wallet is edited properly'''
        add = self.pk
        if add:
            if not self.modified_by:
                errors = {}
                errors.setdefault('modified_by',
                                  []).append(u'You have to specify who is modifying this transaction')
                raise ValidationError(errors)
            else:
                wallet = self.wallet
                if self.is_debit:
                    wallet.debit = self.amount
                else:
                    wallet.credit = self.amount
                wallet.save()
        transaction = self.transaction
        transaction.wallet = True
        transaction.save()
        self.current_balance = self.wallet.balance
        super(WalletTransaction, self).save(*args, **kwargs)
        return self
