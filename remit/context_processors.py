from django.conf import settings
from django.core.urlresolvers import resolve
from accounts.models import Profile
from remit.models import Wallet
from remit.utils import debug


def global_vars(request):
    PAGE_NAME = False
    transactions_left = 0
    try:
        PAGE_NAME = resolve(request.path_info).url_name
    except Exception, e:
        pass

    if PAGE_NAME == 'index':
        PAGE_NAME = 'home'
    logged_in_LINKS = (
        'home', 'transactions', 'phonebook', 'account', 'signout')
    profile = False
    wallet_balance = '0'

    try:
        if request.user.is_authenticated():
            try:
                profile = Profile.objects.get(user=request.user)
            except Exception, e:
                debug(e)

            try:
                wallet, created = Wallet.objects.get_or_create(
                    user=request.user,
                    )
                wallet_balance = wallet.current_balance
            except Exception, e:
                debug(e, 'error getting wallet')
    except Exception, e:
        debug(e)


    return {'APP_EMAILS': settings.APP_EMAILS,'APP_NAME': settings.APP_NAME,'APP_TITLE': settings.APP_TITLE,'DOMAIN_NAME': settings.DOMAIN_NAME ,'BASE_URL': settings.BASE_URL,
            'PAGE_NAME': PAGE_NAME, 'logged_in_LINKS': logged_in_LINKS,
            'user_profile': profile, 'transactions_left': transactions_left,
            'PAGNATION_LIMIT': settings.PAGNATION_LIMIT,'CONTACT_NO':settings.CONTACT_NO,
            'wallet_balance': wallet_balance
            }
