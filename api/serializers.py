from rest_framework import serializers
from accounts.models import Profile
from remit.models import Transaction, Phonebook, Country, Charge, Rate
from django.contrib.auth.models import User



class CountryInfoSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Country
        fields = (
            'currency', 'dailing_code',
        )


class UserInfoSerializer(serializers.HyperlinkedModelSerializer):
    #user_data = serializers.RelatedField(source='user')

    class Meta:
        model = User
        fields = (
            'email',
        )



class RatesSerializer(serializers.ModelSerializer):

    #country = CountryInfoSerializer()

    #add property field
    hashid  = serializers.ReadOnlyField()
    currency  = serializers.ReadOnlyField()
    last_update = serializers.ReadOnlyField()

    class Meta:
        model = Charge
        fields = (
            'currency', 'to_usd', 'to_gbp', 'to_eur',
            'forex_percentage', 'transfer_fee_percentage',
            'transfer_maximum_usd', 'transfer_minimum_usd',
            'mtn_charge', 'airtel_charge', 'tigo_charge',
            'vodafone_charge', 'safaricom_charge', 'orange_charge',
            'general_network_charge','hashid','last_update',
        )



class UserProfileSerializer(serializers.HyperlinkedModelSerializer):

    #serialize user object
    user = UserInfoSerializer()

    #add property field
    avatar  = serializers.ReadOnlyField()

    class Meta:
        model = Profile
        fields = (
            'lastname', 'firstname', 'user','avatar'
        )


class TransactionSerializer(serializers.HyperlinkedModelSerializer):

    hashid  = serializers.ReadOnlyField()
    recipient_number  = serializers.ReadOnlyField()

    class Meta:
        model = Transaction
        fields = (
            'is_processed','amount_sent','amount_received','started_on',
            'processed_on','currency_received' ,'currency_sent', 'hashid',
            'recipient_number',
        )


class SaveTransactionSerializer(serializers.HyperlinkedModelSerializer):

    #hashid  = serializers.ReadOnlyField()
    #recipient_number  = serializers.ReadOnlyField()

    def validate(self, attrs):
        amount_received = attrs.get('amount_received')
        #id = int(attrs.get('transaction_id')) ^ 0xABCDEFAB
        #hashid = attrs.get('transaction_id')
        currency_sent = attrs.get('currency_sent')
        currency_received = attrs.get('currency_received')
        receiver_fname = attrs.get('receiver_fname')
        receiver_lname = attrs.get('receiver_lname')
        visa_success = attrs.get('visa_success')
        visa_processed = attrs.get('visa_processed')
        mobile_reason = attrs.get('mobile_reason')

        if not amount_received or not currency_sent or not currency_received or not receiver_fname or not receiver_lname or not visa_success or not visa_processed or not mobile_reason:

            # msg = ('provide "amount_received" "currency_sent" "currency_received" "receiver_fname" "receiver_lname" "visa_success" "visa_processed" "mobile_reason"')

            raise serializers.ValidationError()
        return attrs





    class Meta:
        model = Transaction
        fields = (
            'amount_received','currency_sent','currency_received','receiver_fname','receiver_lname','visa_success','visa_processed','mobile_reason',
        )


class PhonebookSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Phonebook
        fields = (
            "country_code","ext", "number", "firstname", "lastname",
        )

class GetTransactionIdSerializer(serializers.HyperlinkedModelSerializer):

    def validate(self, attrs):
        print 'validator entered'
        receiver_number = attrs.get('receiver_number')
        amount_sent = attrs.get('amount_sent')

        if not receiver_number or not amount_sent:
            msg = ('Provide "receiver_number" and "amount_sent"')
            raise serializers.ValidationError(msg)

        return attrs
    class Meta:
        model = Transaction
        fields = (
            'receiver_number', 'amount_sent'
        )

class QueryBillSerializer(serializers.HyperlinkedModelSerializer):

    def validate(self,attrs):
        referencenumber = attrs.get('referencenumber')
        receiver_number = attrs.get('receiver_number')
        billtype = attrs.get('billtype')
        amount_sent = attrs.get('amount_sent')

        if not referencenumber or not billtype or not receiver_number or not amount_sent:

            raise serializers.ValidationError()
        return attrs

    class Meta:
        model = Transaction
        fields = ('referencenumber','billtype','receiver_number','amount_sent')

class PayBillSerializer(serializers.HyperlinkedModelSerializer):
    amount_received = ''

    def validate(self,attrs):
        amount_sent = attrs.get('amount_sent')
        transaction_id = attrs.get('transaction_id')
        #amount_received = amount

        if not amount_sent or not transaction_id:
            raise serializers.ValidationError()
        return attrs

    class Meta:
        model = Transaction
        fields = ('amount_sent','')
