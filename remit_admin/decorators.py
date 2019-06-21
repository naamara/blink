'''
Decorators
'''
from django.shortcuts import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Permission
from remit.utils import debug
import remit.settings as settings
from accounts.models import AdminProfile


def admin_required(function):
    '''This page cannot be viewed if a user is not stuff'''
    def wrapper(request, *args, **kw):
        if request.user.is_active and request.user.is_staff:
            #if this is a customer care person we send them back
            profile = AdminProfile.objects.get(user=request.user)
            #if profile.is_customer_care:
            #    return HttpResponseRedirect(reverse('custom_404'))
            return function(request, *args, **kw)
        else:
            return HttpResponseRedirect(reverse('custom_404'))
    return wrapper


def customer_care_required(function):
    '''This page cannot be viewed if a user is not stuff'''
    def wrapper(request, *args, **kw):
        if request.user.is_active and request.user.is_staff:
            #if this is a customer care person we send them back
            if not request.user.is_superuser:
                profile = AdminProfile.objects.get(user=request.user)
                if not profile.is_customer_care:
                    return HttpResponseRedirect(reverse('custom_404'))
            return function(request, *args, **kw)
        else:
            return HttpResponseRedirect(reverse('custom_404'))
    return wrapper


def superuser_required(function):
    '''This page cannot be viewed if a user is not stuff'''
    def wrapper(request, *args, **kw):
        if request.user.is_active and request.user.is_superuser:
            return function(request, *args, **kw)
        else:
            return HttpResponseRedirect(reverse('custom_404'))
    return wrapper


from functools import wraps


def permission_required(codename):
    '''check if a user has particular permissions to access a view'''
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            # Do some stuff
            if request.user.is_active and request.user.is_staff:
                if request.user.is_superuser:
                    return view(request, *args, **kwargs)
                else:
                    try:
                        perm = Permission.objects.filter(
                            user=request.user, codename=codename)
                        #debug(perm,'Permission')
                        if not perm:
                            return HttpResponseRedirect(reverse('admin:admin_dashboard'))
                        return view(request, *args, **kwargs)
                    except Exception, e:
                        if settings.DEBUG:
                            raise e
                        else:
                            debug(e, 'decorator error', 'admin')
                            return HttpResponseRedirect(reverse('admin_503'))
            else:
                return HttpResponseRedirect(reverse('admin:admin_dashboard'))
        return wrapper
    return decorator
