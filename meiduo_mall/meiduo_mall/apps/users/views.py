from django.http.response import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from django_redis import get_redis_connection
from .models import User
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView

from .serializers import UserSerializer


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
