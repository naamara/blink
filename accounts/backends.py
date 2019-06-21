'''
custom authenticated backends
'''
from django.contrib.auth.models import User
from accounts.models import Profile


class EmailVerificationBackend(object):
	""" email verified backend"""


	def authenticate(self, name):
		profile = Profile.objects.get(email_activation_key=name, email_activated=False)
		if profile:
			return profile.user


	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None