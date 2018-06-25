from django.http.response import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from django_redis import get_redis_connection
from .models import User
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework import status
import re

from .serializers import UserSerializer
from verifications.serializers import ImageCodeSerializer
from .utils import get_user_by_account


# 用户名唯一认证
class UserNameCountView(APIView):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count
        }
        return Response(data)


# 手机号唯一认证
class MobileCountView(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'count': count,
            'mobile': mobile
        }
        return Response(data=data)


# 用户注册
class UserRegisterView(CreateAPIView):
    serializer_class = UserSerializer


# 验证账号是否存在，并获取access_token
class SMScodeTokenView(GenericAPIView):
    serializer_class = ImageCodeSerializer

    def get(self, request, account):
        # 验证图片验证码
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 验证手机号是否存在，存在这返回access_token
        user = get_user_by_account(account)
        if user is None:
            return Response({'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 生成access_token
        access_token = user.generate_sms_code_token()

        # 手机号是用户的敏感信息，所以需要处理一下
        mobile = re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', user.mobile)
        return Response({'token': access_token, 'mobile': mobile})
