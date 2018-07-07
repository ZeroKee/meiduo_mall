from rest_framework_extensions.cache.mixins import ListCacheResponseMixin
from rest_framework.generics import ListAPIView

from .serializers import SKUSerializer
from .models import SKU
from . import constants


class HostSKUListView(ListCacheResponseMixin, ListAPIView):
    """
    热销商品使用缓存
    """
    serializer_class = SKUSerializer
    pagination_class = None

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        # 查询集为：当前种类在售销量前三的商品
        return SKU.objects.filter(category_id=category_id, is_launched=True)\
            .order_by('-sales')[:constants.HOT_SKUS_COUNT_LIMIT]
