# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-7-7 下午3:56
from rest_framework import serializers

from .models import SKU


# 返回热销商品详细信息
class SKUSerializer(serializers.ModelSerializer):
    """
    SKU序列化
    """
    class Meta:
        model = SKU
        fields = ['id', 'default_image_url', 'price', 'name','comments']