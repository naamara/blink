'''api views'''
from rest_framework import authentication, permissions, serializers, viewsets, status, generics, parsers, renderers
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from remit.models import Transaction, Phonebook, Charge, Rate, Country
from accounts.models import Profile
from api.serializers import UserProfileSerializer, TransactionSerializer, PhonebookSerializer, RatesSerializer, GetTransactionIdSerializer,SaveTransactionSerializer,QueryBillSerializer,PayBillSerializer
from rest_framework.views import View, APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from remit.utils import debug
from rest_framework.decorators import detail_route, list_route
from api.forms import CcForm
import json
from payments.cc import api_cc
from django.shortcuts import HttpResponse
from payments.mtn import Mtn
#from api.authentication import ApiAuthentication
from api.authentication import ApiAuthentication
#from api.utils import LoggingMixin
from django.utils import timezone
import datetime
from pesapot.pesapot import PesaPot
from decimal import Decimal
#from remit.utils import mailer, sendsms, admin_mail, debug, get_site_admin, get_mobile_network_code
from payments.payment import process_successful_utility

"""
django outh toolkit
"""

class ApiView(APIView):
    """Default Api view class. """
    authentication_classes = (
        authentication.TokenAuthentication,
        authentication.SessionAuthentication,
    )
    #parser_classes = (JSONParser,)  # the parser
    permission_classes = (permissions.IsAuthenticated,)


class DepositMoney(generics.ListAPIView, APIView):

    """
    get rates api ,consumer must provide accces token
    """

    # model = Charge  # Model name
    # serializer_class = RatesSerializer  # Call serializer
    # authentication_classes clear= (
    #    authentication.TokenAuthentication,
    #    )
    parser_classes = (JSONParser,)  # the parser
    permission_classes = ()

    def get(self, request, transactionid, format=None):
        '''check if a number is registered'''
        response = {'status': 0}
        id = int(transactionid) ^ 0xABCDEFAB
        try:
            transaction = Transaction.objects.filter(id=id, user=request.user)
            amount = transaction.amount
            number = transaction.receiver_number
            mtn = Mtn()
            result = mtn.DepositMoney(number, amount, transactionid)
            response = {'status': 0, 'response': result}
        except Exception, e:
            response['error'] = e
        return Response(response)


class CheckNumber(generics.ListAPIView, APIView):

    """
    get rates api ,consumer must provide accces token
    """

    # model = Charge  # Model name
    # serializer_class = RatesSerializer  # Call serializer
    # authentication_classes clear= (
    #    authentication.TokenAuthentication,
    #    )
    parser_classes = (JSONParser,)  # the parser
    # permission_classes = (permissions.IsAuthenticated,)
    permission_classes = ()

    def get(self, request, msisdn, format=None):
        '''check if a number is registered'''
        response = {'status': 0}
        number = msisdn
        mtn = Mtn()
        result = mtn.CheckNumber(number)
        response = {'status': 0, 'response': result}
        return Response(response)


class Rates(generics.ListAPIView, APIView):
    # class Rates(LoggingMixin, APIView):
    """
    get rates api ,consumer must provide accces token
    """

    model = Charge  # Model name
    serializer_class = RatesSerializer  # Call serializer
    authentication_classes = (
        authentication.TokenAuthentication,
    )
    parser_classes = (JSONParser,)  # the parser
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        '''return our user object'''
        rates = Charge.objects.all()
        return rates

    def list(self, request, *args, **kwargs):
        self.object_list = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(
            {'rates': serializer.data}
        )


class CountryRates(Rates):

    """
    get rates api ,consumer must provide accces token
    """

    def get_queryset(self):
        '''return our user object'''
        hashid = int(self.kwargs['hashid'])
        pk = str(hashid ^ 0xABCDEFAB)
        rates = Charge.objects.filter(pk=pk)
        return rates

    def list(self, request, *args, **kwargs):
        self.object_list = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(
            {'rate': serializer.data}
        )


class UserProfile(generics.ListAPIView, APIView):

    """
    get user profile from api ,consumer must provide accces token
    """

    model = Profile  # Model name
    serializer_class = UserProfileSerializer  # Call serializer
    authentication_classes = (
        authentication.TokenAuthentication,
    )
    parser_classes = (JSONParser,)  # the parser
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        '''return our user object'''
        profile = Profile.objects.filter(user=self.request.user.pk)
        return profile

    def list(self, request, *args, **kwargs):
        self.object_list = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(self.object_list, many=True)
        return Response({'profile': serializer.data})


class UserTransactions(generics.ListAPIView, APIView):

    """
    get user Transactions from api ,consumer must provide accces token
    """

    model = Transaction  # Model name
    serializer_class = TransactionSerializer  # Call serializer
    authentication_classes = (
        authentication.TokenAuthentication,
    )
    parser_classes = (JSONParser,)  # the parser
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        '''return all user transactions'''
        transactions = Transaction.objects.filter(user=self.request.user.pk,
                                                  visa_success=True,
                                                  )
        return transactions

    def list(self, request, *args, **kwargs):
        self.object_list = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(self.object_list, many=True)
        return Response({'transactions': serializer.data})


class UserTransaction(UserTransactions):

    """
    get user Transaction from api ,consumer must provide accces token
    """

    def get_queryset(self):
        '''return all user transactions'''
        hashid = int(self.kwargs['hashid'])
        pk = str(hashid ^ 0xABCDEFAB)
        transaction = Transaction.objects.filter(user=self.request.user.pk,
                                                 pk=pk)
        return transaction


class PendingTransactions(UserTransactions):

    def get_queryset(self):
        '''return pending transactions'''
        transactions = Transaction.objects.filter(user=self.request.user.pk,
                                                  visa_success=True,
                                                  is_processed=False,
                                                  )
        return transactions


class CompleteTransactions(UserTransactions):

    def get_queryset(self):
        '''return complete transactions'''
        transactions = Transaction.objects.filter(user=self.request.user.pk,
                                                  visa_success=True, is_processed=True, amount_sent__isnull=False)
        return transactions


class UserPhonebook(generics.ListAPIView, APIView):

    """
    get user phonebook from api ,consumer must provide accces token
    """

    model = Phonebook  # Model name
    serializer_class = PhonebookSerializer  # Call serializer
    authentication_classes = (
        authentication.TokenAuthentication,
    )
    parser_classes = (JSONParser,)  # the parser
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        '''return our user object'''
        phonebook = Phonebook.objects.filter(user=self.request.user.pk)
        return phonebook

    def list(self, request, *args, **kwargs):
        self.object_list = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(self.object_list, many=True)
        return Response(
            {'phonebook': serializer.data}
        )


class UserDoCC(APIView):
    '''do a transaction'''

    model = Transaction
    authentication_classes = (
        authentication.TokenAuthentication,
    )
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        data = CcForm(request.POST)
        if not data.is_valid():
            response = data.errors
        else:
            data = request.POST.copy()
            data['user'] = request.user.pk
            response = api_cc(data, request)
        return HttpResponse(
            json.dumps(response),
            content_type="application/json"
        )


class LoginUser(APIView):
    '''login user option'''
    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.BasicAuthentication
    )
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        try:
            token, created = Token.objects.get_or_create(
                user=self.request.user
            )
            content = {
                'auth': unicode(token.key),
            }
        except Exception:
            pass
        return Response(content)

class GetTransactionId(ApiView):

    """Get transaction id."""
    model = Transaction  # Model name
    serializer_class = GetTransactionIdSerializer

    def post(self,request):
        """transaction id."""
        print ':Within post'
        response = {}

        try:
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid():
                print ':serializer valid'
                post_data = request.POST.copy()
                sender_phone = serializer.validated_data['receiver_number']
                amount_sent = serializer.validated_data['amount_sent']
                amount_sent = int(round(float(amount_sent)))
                try:
                    pass
                except Exception as e:
                    raise
                transaction = Transaction()
                transaction.user = request.user
                temp_user = request.user
                print ':User: ',str(temp_user.__dict__)
                transaction.receiver_number = sender_phone
                transaction.amount_sent = amount_sent
                transaction.added = timezone.now()
                transaction.save()
                response['transaction_id'] = transaction.hashid
                response['status'] = 0

            else:
                print ':Invalid serializer'
                response['errors'] = serializer.errors

        except Exception as e:
            print ':Get Transaction error: ',str(e)

        return Response(response)

class SaveTransaction(ApiView):
    """Save Transaction."""
    model = Transaction
    serializer_class = SaveTransactionSerializer

    def post(self,request):
        """Save transaction."""
        response = {}
        serializer = self.serializer_class(data = request.data)
        transaction_id = None
        post_data = request.POST.copy()

        if serializer.is_valid() and post_data.get('transaction_id', '') == '':
            response['errors'] = 'Provide transaction_id'

        elif serializer.is_valid():
            print ':serializer valid'
            # post_data = request.POST.copy()
            # print ':Post data ',str(post_data)
            transaction_id = post_data.get('transaction_id','')
            print ':transaction_id: ',str(transaction_id)

            amount_received = serializer.validated_data['amount_received']
            #transaction_id = serializer.validated_data['transaction_id']
            currency_sent = serializer.validated_data['currency_sent']
            currency_received = serializer.validated_data['currency_received']
            receiver_fname= serializer.validated_data['receiver_fname']
            receiver_lname = serializer.validated_data['receiver_lname']
            visa_success = serializer.validated_data['visa_success']
            visa_processed = serializer.validated_data['visa_processed']
            mobile_reason = serializer.validated_data['mobile_reason']



            try:
                #transaction = Transaction()
                id = int(transaction_id) ^ 0xABCDEFAB
                transaction  = Transaction.objects.get(id=id)
                print ':Transaction found: '
                transaction.user = request.user
                transaction.amount_received = amount_received
                transaction.currency_sent = currency_sent
                transaction.currency_received = currency_received
                transaction.receiver_fname = receiver_fname
                transaction.receiver_lname = receiver_lname
                transaction.visa_success = visa_success
                transaction.visa_processed = visa_processed
                transaction.mobile_reason = mobile_reason
                transaction.save()
                print ':Transaction saved'
                response['status'] = 'success'

            except Exception as e:
                print ':Transaction failed: ',str(e)
                response['errors'] = 'Failed to save transaction.possible wrong transaction ID'

        else:
            response['errors'] = serializer.errors

        return Response(response)

class QueryBill(ApiView):
    """Get bill account details."""
    model = Transaction
    serializer_class = QueryBillSerializer

    def post(self,request):
        response = {}
        post_data = request.POST.copy()
        serializer = None
        transaction_id = None
        location = None
        billtype = None
        transaction = Transaction()
        account_type = None
        amount_received = None
        country = None
        rate = None
        TWOPLACES = Decimal(10) ** -2

        try:
            billtype  = int(post_data.get('billtype', ''))
        except Exception as e:
            response['errors'] = 'Invalid billtype value. should be 1 or 2'
            return Response(response)

        location = post_data.get('location', '')

        if not post_data.get('billtype',''):
            response['errors'] = 'Provide bill type'
            return Response(response)

        if billtype == 2 and not location:
            response['errors'] = 'Provide location'
            return Response(response)

        if not location:
            location = 'kampala'

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            print ':Serializer valid'
            post_data = serializer.data
            #location = 'kampala'
            refnumber = post_data.get('referencenumber', '')
            billtype = post_data.get('billtype', '')
            receiver_number = post_data.get('receiver_number','')
            amount_sent = post_data.get('amount_sent','')
            amount_sent = float(amount_sent)


            try:
                #from decimal import *
                country = Country.objects.get(code='UG')
                rate = Charge.objects.get(country=country)
                usd = float(rate.to_usd)
                amount_received = float(amount_sent)
                amount_received = usd * amount_sent
                print ':Amount recieved ',str(amount_received)

            except Exception as e:
                print ':Conversion error ',str(e)

            pesapot = PesaPot()
            query_response = None

            try:
                query_response = pesapot.QueryPayBillAccount(
                    referencenumber=refnumber,
                    billtype=billtype,
                    location=location
                )
            except Exception as e:
                raise

            response = query_response.get('result', {})
            print ':Response: ',str(query_response)
            responsecode = response.get('responsecode', 0)

            account_balance = response.get('oustanding_balance', '')
            account_name = response.get('customer_name', '')

            try:
                transaction.referencenumber = refnumber
                transaction.billtype = billtype
                transaction.billarea = location
                transaction.receiver_number = receiver_number
                transaction.utility = True
                transaction.added = timezone.now()
                transaction.user = request.user
                transaction.utility_account_name = account_name
                transaction.amount_sent = amount_sent
                transaction.amount_received = amount_received

                if response.get('customer_type'):
                    transaction.utility_account_type = response.get(
                    'customer_type')
                else:
                    transaction.utility_account_type = "POSTPAID"

                transaction.save()
                transaction_id = transaction.hashid
                response['transaction_id'] = transaction_id
                print '::Transaction data: ',str(transaction.__dict__)
            except Exception as e:
                print ':save transaction error',str(e)

        else:
            print ':Serializer validation failed'
            response['errors'] = serializer.errors

        return Response(response)


class PayBill(ApiView):
    """Pay bill."""
    model = Transaction
    print ':::API pay bill view'
    #serializer_class = PayBillSerializer

    def post(self,request):
        response = {}
        post_data = request.POST.copy()
        serializer = None
        transaction = Transaction()
        transaction_id = post_data.get('transaction_id','')
        pesapot = PesaPot()


        if not transaction_id:
            response['errors'] = 'Provide transaction_id'
            return Response(response)

        try:
            id = int(transaction_id) ^ 0xABCDEFAB
            transaction = Transaction.objects.get(id=id)
            print ':Transaction: ',str(transaction.__dict__)
            print ':Transaction success'

        except Exception as e:
            print ':transaction failed: ',str(e)

        referencenumber = transaction.referencenumber
        amount_received = transaction.amount_received
        phonenumber = transaction.receiver_number
        billtype = transaction.billtype
        names = "".join(transaction.utility_account_name.split())
        paymethod = transaction.utility_account_type
        paid_by = 'useremit'
        area = transaction.billarea
        account_type = transaction.utility_account_type

        try:
            bill_response = pesapot.PayBill(
                referencenumber,
                amount_received,
                phonenumber,
                billtype,
                names,
                account_type,
                area,
            )

            print '::Bill Response ', str(bill_response)
            transaction.mobile_response_metadata = bill_response
            transaction.visa_success = True
            is_processed = False
            transaction.save()
            response['status'] = bill_response

        except Exception as e:
            print '::Pesapot error: ', str(e)
        #return Response(response)
        return Response(bill_response)


class BillStatus(ApiView):
    """
    Get bill transaction status, save to
    mobile response code.
    """
    data_status = None
    useremit_id = None

    def post(self,request):
        data = request.data.copy()
        transaction_response = data.get('transaction_status','')
        useremit_id = data.get('useremit_id','')
        utility_pegpay_id = None
        post_data = None
        transaction = None
        response = {}

        try:
            post_data = json.loads(transaction_response)

        except Exception as e:
            print ':Json load failed ',str(e)

        data_status = post_data.get('status_description', '')
        receipt_id = post_data.get('oustanding_balance', '')
        utility_pegpay_id = post_data.get('pegpay_tran_id','')
        if not utility_pegpay_id:
            utility_pegpay_id = '0'
        print '::receipt_id ', str(receipt_id)
        print '::utility_pegpay_id',str(utility_pegpay_id)

        try:
            vendor_id = post_data.get('vendor_id','')
            #useremit_id = post_data.get('sender_id','')
            #str_id = str(vendor_id)
            str_id = str(useremit_id)
            id = int(str_id) ^ 0xABCDEFAB
            transaction = Transaction.objects.get(id=id)
            print '::TRansaction found, ',str(transaction.__dict__)

        except Exception as e:
            print ':ID error ',str(e)

        if data_status == 'SUCCESS':
            if transaction.utility_account_type == 'PREPAID' and transaction.billtype == '1':
                #data['Yaka Token'] = data['pegpay_tran_id']

                post_data['yaka_token'] = post_data['pegpay_tran_id']

            #transaction.mobile_response_metadata = data
            transaction.mobile_response_metadata = post_data
            transaction.is_processed = True
            transaction.utility_receipt_id = receipt_id
            transaction.utility_pegpay_id = utility_pegpay_id
            transaction.save()

            #process utility and send sms,email
            process_successful_utility(transaction)


        elif data_status == 'FAILED':
            transaction.mobile_response_metadata = post_data
            transaction.save()
            self.post_to_tradelance(post_data)


        #return format_response(request, response, 1, errors)
        return Response(response)
        #return None
