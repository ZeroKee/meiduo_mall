# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-7-1 下午5:08

from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = []
# 使用视图集可以自动生成url
router = DefaultRouter()
# <url前缀, 视图集, 路由名前缀>
router.register(r'areas', views.AreasViewSet, base_name='areas')  # base_name？

urlpatterns += router.urls
