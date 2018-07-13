from django.shortcuts import render
from rest_framework.views import APIView
from .utils import AuthQQ
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.settings import api_settings
from rest_framework.generics import GenericAPIView

from .models import OAuthQQUser
from .exceptions import QQAPIError
from .serializers import OAuthQQUserSerializer
from carts.utils import merge_cart_cookie_to_redis


# GET: /oauth/qq/authorization/?code=xxx
class OAuthQQUrlView(APIView):
    """生成QQ登陆的url地址"""

    def get(self, request):
        # 1. 拼接URl地址
        auth_qq = AuthQQ()
        # 登陆用户在美多
        next_url = request.query_params.get("next", '/')
        url = auth_qq.generate_oauth_qq_url(next_url)

        # 2. 响应前端
        return Response({"auth_url": url})


# /oauth/user/qq/
class QQUserOAuthView(GenericAPIView):
    serializer_class = OAuthQQUserSerializer

    def get(self, request):
        """
        判断QQ登陆用户是否绑定，绑定则返回jwt_token,未绑定则绑定
        :param request:
        :return: 绑定access_token or jwt_token
        """
        code = request.query_params.get('code')
        if not code:
            return Response({"message":"缺少code"}, status=status.HTTP_400_BAD_REQUEST)
        auth = AuthQQ()
        try:
            access_token = auth.get_oauth_access_token(code)
            openid = auth.get_oauth_openid(access_token)
        except QQAPIError:
            return Response({'message': 'QQ服务器错误'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            # 在OAuthQQUser中查询是否有openid
            qq_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 第一次使用qq登陆,返回access_token用于绑定本网站的账号
            token = auth.generate_save_user_token(openid)
            return Response({'access_token':token})
        else:
            # 用户存在则，生成jwt_token
            user = qq_user.user
            # 生成token，并保存在user对象中
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            # 生成载荷
            payload = jwt_payload_handler(user)
            # 生成token
            token = jwt_encode_handler(payload)
            response = Response({
                "user_id":user.id,
                'token':token,
                'username':user.username
            })
            response = merge_cart_cookie_to_redis(request, user, response)
            return response

    def post(self, request):
        """
        绑定绑定本网站的账号，没有注册则创建用户后绑定
        :param request:
        :return: jwt_token
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 生成token，并保存在user对象中
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        # 生成载荷
        payload = jwt_payload_handler(user)
        # 生成token
        token = jwt_encode_handler(payload)
        response = Response({
            "user_id": user.id,
            'token': token,
            'username': user.username
        })
        response = merge_cart_cookie_to_redis(request, user, response)
        return response
