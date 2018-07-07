# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-7-7 下午5:17
from rest_framework import serializers

from goods.models import SKU


class CartSerializer(serializers.Serializer):
    """
    添加到购物车
    """
    sku_id = serializers.IntegerField(label='商品id', required=True, min_value=1)
    count = serializers.IntegerField(label='数量', required=True, min_value=1)
    selected = serializers.BooleanField(label='是否勾选', default=True)

    def validate(self, data):
        sku_id = data['sku_id']
        count = data['count']
        print(count, '这是count')

        # 验证商品是否存在
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            raise serializers.ValidationError({'message':'商品不存在'})
        stock = sku.stock

        # 查询库存是否充足
        if count > stock:
            raise serializers.ValidationError({'message':'商品库存不足'})

        return data


class CartSKUSerializer(serializers.ModelSerializer):
    """
    购物车商品详情
    """
    count = serializers.IntegerField(label='商品数量', required=True, min_value=1)
    selected = serializers.BooleanField(label='勾选状态', default=True)

    class Meta:
        model = SKU
        fields = [
            'id', 'name', 'default_image_url', 'price', 'count', 'selected'
        ]
