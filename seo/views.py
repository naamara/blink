# Create your views here.
'''seo fields'''
#from seo.models import Metadata
from seo.forms import AddSeoForm
from seo.utils import get_metadata_model
from django.template import RequestContext
from django.shortcuts import render_to_response
from remit_admin.decorators import superuser_required
#import remit.settings as settings
from datetime import datetime

@superuser_required
def render_view(request, template, data):
    ''' render_view '''
    '''
    wrapper for rendering views , loads RequestContext
    @request  request object
    @template  string
    @data  tumple
    '''
    return render_to_response(
        template, data,
        context_instance=RequestContext(request)
    )


def seo(request):
    '''get seo'''
    #debug(Metadata,'Seo metadata'
    metadata = get_metadata_model()
    if request.POST:
        metadata.title = request.POST['title']
        metadata.description = request.POST['description']
        metadata.keywords = request.POST['keywords']
        metadata.extras = request.POST['extras']
        metadata.added_by = request.user
        metadata.added_on = datetime.now()
        metadata.save()
    #metadata.description= "ADASdasdasd"
    #metadata.title = "ADASDASdasd"
    #metadata.save()
    form = AddSeoForm(instance=metadata)
    return render_view(request, 'seo.html', {
        'metadata':metadata, 'form':form}
        )