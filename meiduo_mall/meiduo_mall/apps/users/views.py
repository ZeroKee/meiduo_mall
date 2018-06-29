from django.http.response import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework import status
import re
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer, CheckSMSCodeSerializer, CheckPasswordTokenSerializer, UserDetailSerializer, \
    EmailSerializer
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
# POST: /users/(?P<pk>\d+)/password/
class PasswordView(mixins.UpdateModelMixin, GenericAPIView):
    queryset = User.objects.all()
    serializer_class = CheckPasswordTokenSerializer

    def post(self, request, pk):
        return self.update(request, pk)


# 用户登陆认证并返回用户详情
# GET: /user/
class UserDetailView(RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):  # 返回详情视图所需要的模型类对象
        return self.request.user


# 保存邮箱地址并发送邮件
# GET: /emails/
class EmailView(UpdateAPIView):
    serializer_class = EmailSerializer
    # 用户登陆权限认证后，方可验证并保存邮箱
    permission_classes = [IsAuthenticated]

    # 重写get_object方法获取操作对象user,然后传给序列化器的instance
    # request.user获取到的是通过认证全线后的user可以看着jwt_token的载荷user
    def get_object(self):
        return self.request.user


# 验证邮箱
# GET: /emails/verifications/
class VerifyEmailView(APIView):
    def get(self, request):

        # 从查询字符串中拿到access_token
        access_token = request.query_params.get('token')
        if not access_token:
            return Response({'message': '缺少access_token邮箱验证失败'}, status=status.HTTP_400_BAD_REQUEST)

        # 从access_token中获取user
        user = User.verify_email_token(access_token)
        if user is None:
            return Response({'message': '无效的access_token邮箱验证失败'}, status=status.HTTP_400_BAD_REQUEST)

        # 修改user的email_active 状态
        user.email_active = True
        user.save()
        return Response({'message': '邮箱验证成功'})
