# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-7-13 下午3:29
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^orders/settlement/$", views.OrderSettlementView.as_view()),
    url(r"^orders/$", views.SaveOrderView.as_view()),

]
