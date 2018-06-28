# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-6-20 下午4:53
from django.conf.urls import url

from . import views
urlpatterns = [
    url(r'^image_code/(?P<image_code_id>.+)/$', views.ImageCodeView.as_view()),
    url(r'^sms_code/(?P<mobile>1[3-9]\d{9})/$', views.SmsCodeView.as_view()),
    url(r'^sms_code/$', views.SMSCodeByTokenView.as_view()),
]