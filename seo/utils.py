'''seo utils'''
from django.contrib.sites.models import Site
from seo.models import Metadata
from remit.utils import debug
from django.conf import settings



def get_metadata_model():
    '''return metadata model'''
    metadata = False
    try:
        metadata = Metadata.objects.get(pk=1)
    except Exception, e:
        debug(e)
        # create the rates if we don't have them
    if not metadata:
        metadata = Metadata.objects.create(site=Site.objects.get_current(),
            pk=1,title=settings.APP_TITLE,
            description=settings.APP_TITLE,
            keywords=settings.APP_TITLE
            )
        metadata.save()
    return metadata