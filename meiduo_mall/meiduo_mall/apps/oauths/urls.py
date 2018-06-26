# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-6-26 下午4:38
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^qq/authorization/$', views.OAuthQQUrlView.as_view())
]
