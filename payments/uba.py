'''uba payments , json response'''
import remit.settings as settings
from datetime import datetime
import requests
from BeautifulSoup import BeautifulSoup
from remit.utils import debug


class uba():
	"""Handle payments for uba"""


	def __init__(self):
		self.api_username = settings.YOPAY_USERNAME
		self.api_password = settings.YOPAY_PASSWORD
		self.api_endpoint = settings.YOPAY_ENDPOINT

	def get_transaction_id(self):
		transaction_id = ''
		self.transaction_id = transaction_id
		return transaction_id

	def confirm_transaction(self,transaction_id):
		'''confirm the transaction_id we received from uba'''
		if not self.transaction_id == transaction_id:
			return False
		else:
			'''fetch the user details'''
			return True
