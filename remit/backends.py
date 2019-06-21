from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class EmailAuthBackend(object):
    """
    Email Authentication Backend
    
    Allows a user to sign in using an email/username password pair
    """
    
    def authenticate(self, username=None, password=None):
        """ Authenticate a user based on email address as the user name. """

        try:
            validate_email(username)
            kwargs = {'email': username}
        except ValidationError:
            kwargs = {'username': username}

        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None 

    def get_user(self, user_id):
        """ Get a User object from the user_id. """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None