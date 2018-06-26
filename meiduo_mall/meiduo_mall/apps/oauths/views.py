from django.shortcuts import render
from rest_framework.views import APIView
from .utils import AuthQQ
from rest_framework.response import Response


# Create your views here.
class OAuthQQUrlView(APIView):
    """生成QQ登陆的url地址"""
    def get(self,request):
        # 1. 拼接URl地址
        auth_qq = AuthQQ()
        # 登陆用户在美多
        next_url = request.query_params.get("next", '/')
        url = auth_qq.generate_oauth_qq_url(next_url)

        # 2. 响应前端
        return Response({"auth_url": url})