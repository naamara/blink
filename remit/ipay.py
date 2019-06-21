'''Handle CC payments for IPay'''
import remit.payments as p

def ipay_hash(p):
    import hmac, hashlib
    #from hashlib import sha1
    #h = hmac.new(settings.IPAY_HASH_KEY, '', sha1)
    ## add content
    data = '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s'%(
        p['live'],p['mm'],p['mb'],p['dc'],p['cc'],p['mer'],p['oid'],p['inv'],p['ttl'],p['tel'],p['eml'],p['vid'],
        p['cur'],p['p1'],p['p2'],p['p3'],p['p4'],p['cbk'],p['cst'],p['crl'])
    debug(data, 'data string')
    #h.update(content) 
    #hash_key = h.hexdigest()
    hash_key = hmac.new(settings.IPAY_HASH_KEY, data, hashlib.sha1).hexdigest()
    return hash_key

@login_required
def do_cc(request, data):
    '''
    handles the processing the cc
    @request  request object
    '''
    process_cc = True
    amount_sent = p.our_charge(data.amount_sent)
    url = 'https://www.ipayafrica.com/payments/'
    params = {'live':settings.LIVE,'mer':settings.IPAY_MERCHANT,'oid':data.get_order_id(),'inv':data.get_invoice(),
        'ttl':amount_sent,'tel':request.user.profile.get_phonenumber(),'eml':request.user.email,'vid':settings.IPAY_USER,'cur':'USD',
        'cbk':settings.IPAY_CALLBACK_URL,'cst':0,'hsh':settings.IPAY_HASH_KEY,
        'mm':0,'mb':0,'dc':1,'cc':1,'p1':'','p2':'','p3':'','p4':'','crl':0}
    params['hsh'] = ipay_hash(params)
    params = urllib.urlencode(params)
    cc_link = "%s?%s" % (url, params)
    debug(cc_link)