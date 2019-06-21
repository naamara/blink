'''bitcoin views'''
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from btc.cryptocharts import btc_to_ugx,btc_to_usd


def render_view(request, template, data):
    ''' render_view '''
    '''
    wrapper for rendering views , loads RequestContext
    @request  request object
    @template  string
    @data  tumple
    '''
    data.update({'btc_to_ugx':btc_to_ugx(price=1),
        'btc_to_usd':btc_to_usd}
        )
    return render_to_response(
        template, data,
        context_instance=RequestContext(request)
    )

def home(request):
	'''render home views'''
	return render_view(request, 'bitcoin.html', {})


@login_required
def send_bitcoin(request):
	'''render send bitcoin views'''
	return render_view(request, 
		'send_bitcoin.html', 
		{})