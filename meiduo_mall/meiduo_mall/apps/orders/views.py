from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from django_redis import get_redis_connection
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from decimal import Decimal

from goods.models import SKU
from . import serializers


class OrderSettlementView(APIView):
    """
    GET: orders/settlement/
    获取购物商品信息
    """
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        user = request.user
        redis_conn = get_redis_connection("cart")
        redis_cart = redis_conn.hgetall("cart_%s" % user.id)
        redis_cart_selected = redis_conn.smembers("cart_selected_%s" % user.id)

        # 给sku添加count属性
        cart = {}

        for sku_id in redis_cart_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])

        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]

        # 运费
        freight = Decimal("10.00")

        serializer = serializers.OrderSettlementSerializer({"freight": freight, "skus": skus})
        return Response(serializer.data)


class SaveOrderView(CreateAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = serializers.SaveOrderSerializer
