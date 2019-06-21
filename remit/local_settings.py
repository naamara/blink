
ALLOWED_HOSTS = [ 'https://simtransfer.com', 'simtransfer.com','www.simtransfer.com']
#DEBUG = 1
OTHER_FEES = 1

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEBUG_PAYMENTS = DEBUG

APP_NAME = 'B-link'
DOMAIN_NAME = 'B-link'
APP_TITLE = 'B-link | Giving basics skills to Ugandans | The best online Health information provider'

#MANAGERS = ADMINS

#BASE_URL = 'http://127.0.0.1/useremit/'
BASE_URL = 'http://127.0.0.1:8000/'

import os
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir)) + '/'


DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.sqlite3',
        # Or path to database file if using sqlite3.
        #'NAME': 'simtransferdevdb',
        #'NAME': 'os.path.join(BASE_DIR + 'run',"db.sqlite3")',
        'NAME': os.path.join(BASE_DIR + 'run', 'db.sqlite3'),
        # The following settings are not used with sqlite3:
        #'USER': 'postgres',
        #'PASSWORD': '6@!&*842f85',
        # Empty for localhost through domain sockets or '127.0.0.1' for
        # localhost through TCP.
        'HOST': 'LOCALHOST',
        'PORT': '',                      # Set to empty string for default.
        #'OPTIONS': {'autocommit': True, },
    }
}



#DATABASES = {
#    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#        'ENGINE': 'django.db.backends.sqlite3',

        # Or path to database file if using sqlite3.
#        'NAME': os.path.join(BASE_DIR + 'run', 'test.db'),
#    }
#}

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = BASE_URL + 'static/uploads/'

# Ipay
#LIVE = 0
IPAY_CALLBACK_URL = BASE_URL + 'transaction/confirm_payment/'
#IPAY_USER = 'demo'
#IPAY_MERCHANT = 'RedCore Demo'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '%sstatic/' % BASE_URL


SSLIFY_DISABLE = True

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

USE_JUMIO = False
PAYBILL = True

# Pesapot
PESAPOT_URL = 'http://pesapot.com/api/'
PESAPOT_TOKEN = '2b93cb0b9aace9a874ec3c3d2c70a8fcc0ec2c5e'
PESAPOT_KEY = '2b93cb0b9aace9a874ec3c3d2c70a8fcc0ec2c5e'
