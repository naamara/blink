"""
Remit Tests
run with "manage.py test".
"""

from django.utils import unittest
import converter
from remit.utils import mailer, sendsms, admin_mail
from remit.models import Transaction, Rate
from accounts.models import Profile
from django.test.client import RequestFactory
from django.contrib.auth.models import User
from remit.converter import convert
import remit.payment as p
from django.contrib.sites.models import Site


class ConverterTestCase(unittest.TestCase):
    
    def test_usd(self):
        usd = converter.convert('usd', 'USD', 1.00)
        self.assertEquals(usd, 1.0)
        
    def test_jpy(self):
        jpy = converter.convert('usd', 'jpy', 1.00)
        self.assertEquals(type(u'1.0'), type(jpy))
        self.assertNotEquals(jpy, u'0.000')
    
    def test_dummy_currency(self):
        foo = converter.convert('usd', 'foo', 1.00)
        self.assertEquals(foo, u'0.000')


class TestUtils(unittest.TestCase):
    '''
    Test utils
    '''
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.factory.user = User.objects.create(username='testuser')
        self.factory.profile = Profile.objects.create(user=self.factory.user, firstname='Test', lastname='user')

    def test_admin_mailer(self):
        request = self.factory.get('/home')
        self.assertEquals(True, admin_mail(request, 'user_verification', self.factory.profile))

    def test_admin_mailer_fail(self):
        request = self.factory.get('/home')
        transaction = Transaction.objects.filter(id=78)
        self.assertEquals(False, admin_mail(request, 'fake_email', transaction))

    def tearDown(self):
        self.factory.user.delete()
        self.factory.profile.delete()


class TestModels(unittest.TestCase):
    '''
    Test Models
    '''
    def setUp(self):
        # Every test needs access to the request factory.
        #self.factory = RequestFactory()
        self.user = User.objects.create(username='testuser')
        self.rate = Rate.objects.create(user=self.user)

    def test_get_default_rate(self):
        self.assertEquals(self.rate.usd_to_ugx, self.rate.get_default_rate('USD', 'UGX'))

    def tearDown(self):
        self.user.delete()
        self.rate.delete()


class TestCurrencyConverter(unittest.TestCase):
    '''
    Tests for the currency converter
    '''

    def setUp(self):
        # Every test needs access to the request factory.
        #self.factory = RequestFactory()
        self.user = User.objects.create(username='testuser')
        self.rate = Rate.objects.create(user=self.user)

    def test_convert_currency(self):
        self.assertEquals(self.rate.usd_to_ugx,convert(from_curr='USD', to_curr='UGX'))

    def tearDown(self):
        self.user.delete()
        self.rate.delete()


class TestTransactions(unittest.TestCase):
    '''
    Tests for the currency converter
    '''

    def setUp(self):
        # Every test needs access to the request factory.
        #self.factory = RequestFactory()
        self.user = User.objects.create(username='testuser')
        self.transaction = Transaction.objects.create(user=self.user)

    def test_visa_transactions(self):
        data = {}
        p.process_visa(self.transaction, data)

    def tearDown(self):
        self.user.delete()
        self.rate.delete()



class TestEmails(unittest.TestCase):
    '''
    Tests for the currency converter
    '''

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.factory.user = User.objects.create(username='testuser',email="madradavid@gmail.com")
        self.factory.profile = Profile.objects.create(user=self.factory.user, firstname='Test', lastname='user')
        self.rates = Rate(site=Site.objects.get_current(),user=self.factory.user)
        self.rates.save()
        self.transaction = Transaction.objects.create(user=self.factory.user,
            amount_sent=3333,amount_received=333333)


    def test_card_charged_email(self):
        '''test card charged email'''
        p.card_charged_email(self.factory, self.transaction)

    def tearDown(self):
        self.transaction.delete()
        self.rates.delete()