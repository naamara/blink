"""
model managers
"""
from django.db import models


class TransactionQuerySet(models.QuerySet):

    def pending(self):
        return self.filter(visa_success=True,
        	is_processed=False,
        	amount_sent__isnull=False,
        	)

    def successful(self):
        return self.filter(visa_success=True,
        	is_processed=True, 
        	amount_sent__isnull=False
        	)

    def failed(self):
        return self.filter(visa_success=False)


class MobileMoneyTransactionManager(models.Manager):
    def get_queryset(self):
        return TransactionQuerySet(
        	self.model, using=self._db).filter(
        	utility=False,
        	wallet=False
        	)

    def pending(self):
        return self.get_queryset().pending()

    def successful(self):
        return self.get_queryset().successful()

    def failed(self):
        return self.get_queryset().failed()


class BillPaymentTransactionManager(models.Manager):
    def get_queryset(self):
        return TransactionQuerySet(
        	self.model, using=self._db).filter(
        	utility=True,
        	wallet=False
        	)

    def pending(self):
        return self.get_queryset().pending()

    def successful(self):
        return self.get_queryset().successful()

    def failed(self):
        return self.get_queryset().failed()