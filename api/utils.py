"""
Utitilities for api
"""
from django.conf import settings
import logging
from django.core import exceptions
# Get an instance of a logger
logger = logging.getLogger()


class LoggingMixin(object):

    def finalize_response(self, request, response, *args, **kwargs):
        # do the logging
        if settings.DEBUG:
            logger.debug("[{0}] {1}".format(
                self.__class__.__name__, response.data))
        return super(LoggingMixin, self).finalize_response(
            request, response, *args, **kwargs
        )

    def initial(self, request, *args, **kwargs):
        # do the logging
        if settings.DEBUG:
            try:
                data = request._data
                logger.debug("[{0}] {1}".format(self.__class__.__name__, data))
            except exceptions.ParseError:
                data = '[Invalid data in request]'

        super(LoggingMixin, self).initial(request, *args, **kwargs)
