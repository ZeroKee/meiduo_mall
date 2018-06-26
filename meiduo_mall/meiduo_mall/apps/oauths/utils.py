# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-6-26 下午4:40
from urllib.parse import urlencode
from django.conf import settings


class AuthQQ:
    """
    QQ第三方登陆工具类
    里面写上关于QQ登陆的方法和属性
    """
    def __init__(self):
        self.app_id = settings.QQ_APP_ID
        self.app_key = settings.QQ_APP_KEY
        self.redirect_uri = settings.QQ_REDIRECT_URI

    def generate_oauth_qq_url(self, state):
        """
        生成QQ第三方登陆的url地址
        :param state: 跳转地址或其他登陆页面需要的参数
        :return: 登陆地址
        """
        """"""
        # 1. 组装url地址[不能漏了问号！！！]
        base_url = "https://graph.qq.com/oauth2.0/authorize" + "?"
        query_params = {
            "response_type": "code",
            "client_id":  self.app_id,  # app_id
            "redirect_uri": self.redirect_uri,
            "state": state, # 登陆成功以后跳转地址 next参数的只
            "scope": "get_user_info", # 接口名称[固定]
        }
        # 把字典组装成查询字符串
        # response_type=code&client_id=101486400&....
        query_string = urlencode(query_params)
        url = base_url + query_string
        return url