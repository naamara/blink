''' Admin Utils '''
from accounts.models import Profile
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from accounts.forms import LoginInfoForm, UserActionsForm, LogEntryForm
from remit.utils import debug


LOG_ACTION = {
'ADDITION':1,'CHANGE':2,'DELETION':3,'VIEW':4,
'SEARCH':5,'VIEW_TRANSACTION':6,'EDIT_TRANSACTION':7,
'VIEW_USER':8,'VERIFY_USER':9,'LOGIN':10,'LOGOUT':11,'PROCESS_TRANSACTION':12,
'SEARCH_USERS':13,'VIEW_AUDIT_TRAILS':14,' BLOCK_USER':15
}

def users_pending_verification(count=False):
    '''get pending users'''
    user_list = Profile.objects.filter(
        ~Q(id_pic=''), account_verified=False, id_verified=False, account_blocked=False, phone_verified=True)
    if count:
        user_list = user_list.count()
    return user_list


def verified_users(count=False):
    '''get pending users'''
    user_list = Profile.objects.filter(
        account_verified=True, id_verified=True, account_blocked=False,
        user__isnull=False)
    if count:
        user_list = user_list.count()
    return user_list


def unverified_users(count=False):
    '''get pending users'''
    user_list = Profile.objects.filter(Q(id_pic=''),account_verified=False, id_verified=False, account_blocked=False,user__isnull=False)
    if count:
        user_list = user_list.count()
    return user_list


def blocked_users(count=False):
    '''get pending users'''
    user_list = Profile.objects.filter(
        account_blocked=True, user__isnull=False)
    if count:
        user_list = user_list.count()
    return user_list



def store_login_info(request):
    '''store login information'''
    try:
        meta = request.META.copy()
        data = {'user_agent':meta.pop('HTTP_USER_AGENT', None)}
        data['remote_addr'] = meta.pop('REMOTE_ADDR', None)
        data['user'] = request.user.pk
        form = LoginInfoForm(data)
        if form.is_valid():
            obj = form.save()
            request.session['login_info'] = obj.pk
        else:
            debug(form.errors,'Session Info Save')
    except Exception, e:
        debug(e,'Session Info Save')
    log_action(request, model_object=request.user, action_flag=10, change_message='Logged In')


def log_action(request, model_object, action_flag, change_message=''):
    '''log user actions'''

    logdata = {}
    path = request.get_full_path()
    change_message = '%s via <a href="%s">%s</a> ' % (change_message, path, path )
    try:
        logdata['user'] = request.user.id
        logdata['action_flag'] = action_flag
        logdata['change_message'] = change_message
        logdata['object_repr'] = unicode(model_object)[:200]
    except Exception, e:
        debug(e,'logdata error')
        pass


    try:
        logdata['content_type'] = ContentType.objects.get_for_model(model_object).pk
        logdata['object_id'] = model_object.id
    except Exception, e:
        debug(e,'logdata save error')
        pass
    

    logform = LogEntryForm(logdata)
    if logform.is_valid():
        obj = logform.save()        
        try:
            data = {'log_entry':obj.pk, 'user':request.user.pk}
            if not 'login_info' in request.session:
                store_login_info(request)
            data['session'] = request.session['login_info']
            form = UserActionsForm(data)
            if form.is_valid():
                form.save()
            else:
                debug(form.errors,'Log Action Save')
        except Exception, e:
            debug(e, 'Log Action Save')
    else:
        debug(logform.errors,'Log Action Save errors')
        #pass
    

