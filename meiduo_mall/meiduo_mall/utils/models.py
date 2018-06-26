# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-6-26 下午4:45
from django.db import models


class BaseModel(models.Model):
    create_time=models.DateField(verbose_name='创建时间', auto_now_add=True)
    update_time=models.DateField(verbose_name='修改时间', auto_now=True)

    class Meta:
        abstract = True  # 声明该模型类为抽象类，不需要迁移建表