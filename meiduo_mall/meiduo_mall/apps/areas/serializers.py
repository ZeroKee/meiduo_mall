# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-7-1 下午4:22
from rest_framework import serializers

from .models import Areas


# 返回所有省
class AreaSerializer(serializers.ModelSerializer):
    """
    行政区划信息
    """
    class Meta:
        model = Areas
        fields = ['id', 'name']


# 根据省返回所有的市， 根据市返回所有的区
class SubAreaSerializer(serializers.ModelSerializer):
    """
    子行政区划信息
    """
    subs = AreaSerializer(many=True, read_only=True)  # 当返回的字段数据不只一个，有多个时使用many选项

    class Meta:
        model = Areas
        fields = ['id', 'name', 'subs']