# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-6-20 下午2:53
from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r'^username/(?P<username>\w{5,20})/count/$', views.UserNameCountView.as_view()),
    url(r'^mobile/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    url(r'^users/$', views.UserRegisterView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token, name='authorizations'),
    url(r'^accounts/(?P<account>\w{5,20})/sms/token/$', views.SMScodeTokenView.as_view()),
]