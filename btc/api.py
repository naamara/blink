from btc.models import TradingPair
from rest_framework import viewsets, routers
from django.conf.urls import patterns, include, url
from btc.serializers import TradingPairSerializer


# ViewSets define the view behavior.
class TradingPairViewSet(viewsets.ModelViewSet):
    model = TradingPair
    serializer_class = TradingPairSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = TradingPair.objects.all().order_by('-id')
        pair = self.request.QUERY_PARAMS.get('pair', None)
        limit = self.request.QUERY_PARAMS.get('limit', None)
        if pair is not None:
            queryset = queryset.filter(pair=pair)
        if limit is not None:
            limit = unicode(limit)
            if limit.isnumeric():
                queryset = queryset[:limit]
        return queryset

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'tradingpairs', TradingPairViewSet)
router.register(r'tradingpairs/(\w+)', TradingPairViewSet)


# For Rest Framework
urlpatterns = patterns('',
                       url(r'^api/', include(router.urls)),
                       )
