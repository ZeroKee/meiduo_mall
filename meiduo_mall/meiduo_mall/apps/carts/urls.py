# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-7-7 下午6:44
from rest_framework.urls import url

from . import views

urlpatterns =[
    url(r'^cart/$', views.CartView.as_view())
]
