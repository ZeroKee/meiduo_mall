# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-6-23 下午8:01
import re
from .models import User
from django.contrib.auth.backends import ModelBackend


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    jwt登陆认证默认只返回token，需要重写加载载荷的方法返回user_id, user_name
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_account(account):
    """
    用户可能使用用户名登陆或者手机号登陆
    :param account: 登陆名
    :return: 返回user对象
    """
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    # 没查询到对象，说明用户名不存在
    except User.DoesNotExist:
        user = None
    return user


# jwt原有的登陆认证系统， 默认是认证username, password，因为登陆名现在不确定了，
# 所以需要修改认证方法 authorization
class UsernameMobileAuthBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        if user is not None and user.check_password(password):
            return user
