from django.http.response import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework import status
import re
from rest_framework import mixins

from .serializers import UserSerializer, CheckSMSCodeSerializer, CheckPasswordTokenSerializer
from verifications.serializers import ImageCodeSerializer
from .utils import get_user_by_account
from .models import User


# 用户名唯一认证
# GET: /username/(?P<username>\w{5,20})/count/
class UserNameCountView(APIView):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            'username': username,
            'count': count
        }
        return Response(data)


# 手机号唯一认证
# GET: /mobile/(?P<mobile>1[3-9]\d{9})/count/
class MobileCountView(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            'count': count,
            'mobile': mobile
        }
        return Response(data=data)


# 用户注册
# POST: /users/
class UserRegisterView(CreateAPIView):
    serializer_class = UserSerializer


# 验证账号是否存在，并获取access_token
# GET: /accounts/(?P<account>\w{5,20})/sms/token
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
        return Response({'access_token': access_token, 'mobile': mobile})


# 验证短信验证码，并返回重置密码所需要的access_token
# GET: /accounts/(?P<account>\w{5,20}/password/token/?sms_code=xxx)
class PasswordTokenView(GenericAPIView):
    serializer_class = CheckSMSCodeSerializer

    def get(self, request, account):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = serializer.user
        # 验证通过，生成重置密码所需要的access_token
        access_token = user.generate_password_token()

        return Response({'access_token': access_token, 'user_id': user.id})


# 验证access_token并且重置密码
class PasswordView(mixins.UpdateModelMixin, GenericAPIView):
    queryset = User.objects.all()
    serializer_class = CheckPasswordTokenSerializer

    def post(self, request, pk):
        return self.update(request, pk)



