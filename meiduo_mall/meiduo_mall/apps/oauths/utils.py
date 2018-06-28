# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-6-26 下午4:40
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen
from django.conf import settings
import json
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSerializer,BadData

from . import constants


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
            "client_id": self.app_id,  # app_id
            "redirect_uri": self.redirect_uri,
            "state": state,  # 登陆成功以后跳转地址 next参数的只
            "scope": "get_user_info",  # 接口名称[固定]
        }
        # 把字典组装成查询字符串
        # response_type=code&client_id=101486400&....
        query_string = urlencode(query_params)
        url = base_url + query_string
        return url

    def get_oauth_access_token(self, code):
        """
        获取得到openid的access_token
        :param code: QQ服务器返回的code
        :return: access_token
        """
        # 1. 组装url地址[不能漏了问号！！！]
        base_url = "https://graph.qq.com/oauth2.0/token" + "?"
        query_params = {
            "grant_type": "authorization_code",
            "client_id": self.app_id,
            # "redirect_uri": self.redirect_uri + '?state=' + state,
            "redirect_uri": self.redirect_uri,
            "code": code,
            "client_secret": self.app_key,
        }
        # 将字典数据转化为查询字符串
        query_params = urlencode(query_params)
        url = base_url + query_params
        # 获取响应
        response_data = urlopen(url).read().decode()
        # 获取access_token
        access_token = parse_qs(response_data).get('access_token')[0]

        return access_token

    def get_oauth_openid(self, access_token):
        """
        获取QQ登陆用户在第三方网站的唯一标示
        :param access_token: 获取openid的access_token
        :return: openid
        """
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token
        # callback( {"client_id":"101486400","openid":"58B233E74A89874B32884001C39C88E8"} );\n
        response_data = urlopen(url).read().decode()
        response_json = response_data[10: -4]
        response_dict = json.loads(response_json)
        openid = response_dict['openid']

        return openid

    def generate_save_user_token(self, openid):
        """
        生成绑定账号的access_token
        :param openid: QQ服务器返回的openid
        :return: access_token
        """
        serializer = TJWSerializer(settings.SECRET_KEY, constants.SAVE_USER_TOKEN_EXPIRES)
        token = serializer.dumps({'openid': openid})
        # 把bytes转成字符串
        token = token.decode()
        return token

    @staticmethod
    def check_save_user_token(access_token):
        """
        检查access_token中是否有openid
        :param access_token: access_token
        :return: openid or None
        """
        serializer = TJWSerializer(settings.SECRET_KEY, constants.SAVE_USER_TOKEN_EXPIRES)
        try:
            data = serializer.loads(access_token)
        except BadData:
            return None
        return data.get('openid')