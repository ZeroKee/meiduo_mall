# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-7-7 下午4:28
from rest_framework.urls import url

from . import views

urlpatterns = [
    url(r'^categories/(?P<category_id>\d+)/hotskus/$', views.HostSKUListView.as_view())
]