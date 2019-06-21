'''Metadata Tags'''
from django.template import Library
register = Library()
#from seo.models import Metadata
from seo.utils import get_metadata_model


@register.simple_tag
def load_metadata():
    #metadata = Metadata.objects.get(pk=1)
    metadata = get_metadata_model()
    tags = '%s\n%s\n\n%s' %(metadata.get_keywords(),
        metadata.get_description(),
        metadata.get_extras())
    return tags


@register.simple_tag
def load_title():
    #metadata = Metadata.objects.get(pk=1)
    metadata = get_metadata_model()
    tags = '%s\n' %(metadata.get_title())
    return tags