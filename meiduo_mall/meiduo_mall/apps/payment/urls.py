# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-7-13 下午7:50
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^orders/(?P<order_id>\d+)/payment/$", views.PaymentView.as_view()),
    url(r"^payment/status/$", views.PaymentStatusView.as_view())
]