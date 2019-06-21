'''SEO Field '''
from django.db import models


class MetaTagField(models.Field):

    description = "Field to add metatags"
    __metaclass__ = models.SubfieldBase


    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 200
        super(MetaTagField, self).__init__(*args, **kwargs)

    def db_type(self, connection):
        return models.CharField


    def to_python(self, value):
        return u'<%s>%s</%s>' % (self.name, value, self.name)


    def value_to_string(self, instance):
        metatag = getattr(instance, self.name)
        if metatag:
            return metatag
        return None