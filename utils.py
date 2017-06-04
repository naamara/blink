''' Account Utilities '''
import remit.settings as settings
import MySQLdb
from django.contrib.auth.models import User
from accounts.models import Profile
from remit.utils import generate_sha1


def migrate_user_login(data):
    ''' Docstring '''
    user = None
    db = MySQLdb.connect(host=settings.OLD_DB_HOST,  # your host, usually localhost
                         user=settings.OLD_DB_USER,  # your username
                         # your password
                         passwd=settings.OLD_DB_PASS,
                         db=settings.OLD_DB_NAME)  # name of the data base
        # you must create a Cursor object. It will let
        # you execute all the queries you need
    cur = db.cursor()
    # check if the users credetials are right
    login = cur.execute(
        'SELECT userid from login where passkey = password("%s%s") AND pass = password("%s%s")' % (
        settings.OLD_DB_SALT, data[
            'email'], settings.OLD_DB_SALT, data['password']
        )
    )
    if login:
        userid = cur.fetchone()
        userid = userid[0]
        # get the user and migrate thier login details
        user = User.objects.get(email=data['email'])
        if user:
            try:
                user.set_password(data['password'])
                user.save()
            except Exception, e:
                print e
    return user

try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
    get_user_model = lambda: User


def change_email(username, newemail):
    '''update user email'''
    update = get_user_model().objects.filter(
        username=username).update(email=newemail)
    if update:
        user = User.objects.get(email__iexact=newemail)
        return generate_email_confirmation_key(user)


def generate_email_confirmation_key(user, key_only=False):
    '''create and save a confirmation key'''
    try:
        email = user.email
        salt, email_confirmation_key = generate_sha1(
            email, user.username)
        if not key_only:
            profile = Profile.objects.get(user=user)
            profile.email_activation_key = email_confirmation_key
            profile.email_activated = False
            profile.save()
    except Exception, e:
        print e
        email_confirmation_key = False
    return email_confirmation_key
