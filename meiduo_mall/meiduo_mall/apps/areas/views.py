from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.mixins import CacheResponseMixin

from .serializers import AreaSerializer, SubAreaSerializer
from .models import Areas


# 行政区划，返回对应的省，市，区
class AreasViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    pagination_class = None  # 指明该视图返回的数据不需要执行配置中的分页操作(后面商品列表需要分页)

    def get_serializer_class(self):
        """根据请求动作来确定序列化器"""
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubAreaSerializer

    def get_queryset(self):
        """根据序列化动作来确定查询集"""
        if self.action=='list':
            return Areas.objects.filter(parent_id=None)
        else:
            return Areas.objects.all()

