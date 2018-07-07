import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework import status
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.views import ObtainJSONWebToken

from .serializers import UserSerializer, CheckSMSCodeSerializer, CheckPasswordTokenSerializer, UserDetailSerializer, \
    EmailSerializer, CheckPasswordSerializer, AddressSerializer, AddressesTitleSerializer
from verifications.serializers import ImageCodeSerializer
from .utils import get_user_by_account
from .models import User, Address
from . import constants
from carts.utils import merge_cart_cookie_to_redis


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


# 登陆验证并修改密码
# PUT: /users/password/
class ChangePasswordView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = CheckPasswordSerializer
    permission_classes = [IsAuthenticated]  # 指定认证类

    def get_object(self):  # 返回认证后的user对象
        return self.request.user


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


# 收货地址
class AddressViewSet(ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(is_deleted=False)

    # POST: /addresses/ 新增地址
    def create(self, request, *args, **kwargs):
        # 判断地址是否已经达到上线　最多20个
        count = request.user.addresses.count()
        if count > constants.USER_ADDRESSES_COUNT:
            return Response({'message': '用户地址已达上限'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    # PUT: /addresses/(?P<pk>\d+/) 修改地址　　这个动作可以不用写，因为ModelViewSet已经将６种功能集成了，不需要重写的功能可以直接使用
    # def update(self, request, *args, **kwargs):
    #     return super().update(request, *args, **kwargs)

    # GET: /addresses/ 获取所有地址
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # DELETE: /addresses/(?P<pk>\d+)/ 逻辑删除地址
    def destroy(self, request, *args, **kwargs):
        address = self.get_object()
        address.is_deleted = True
        address.save()
        return Response({'message': '删除地址成功'}, status=status.HTTP_204_NO_CONTENT)

    # PUT： /addresses/(?P<pk>\d+)/status/ 设置默认地址
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None, address_id=None):
        # 在url中传递pk值，相应的扩展类就可以通过get_object()拿到这个对象
        address = self.get_object()
        user = request.user
        user.default_address = address
        user.save()
        return Response({'message':'设置默认地址成功'}, status=status.HTTP_200_OK)

    # GET: /addresses/(?P<pk>\d+)/show/  返回标题信息
    # @action(methods=['get'], detail=True)
    # def show(self, request, pk=None, address_id=None):
    #     address = self.get_object()
    #     serializer = AddressesTitleSerializer(instance=address)
    #     return Response(data=serializer.data, status=status.HTTP_200_OK)

    # PUT: /addresses/(?P<pk>\d+)/edit/
    @action(methods=['put'], detail=True)
    def edit(self, request, pk=None, address_id=None):
        address = self.get_object()
        serializer = AddressesTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)


# 重写登陆视图，登陆自动合并购物车
class UserAuthorizeView(ObtainJSONWebToken):
    """重写jwt的登陆视图"""
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # 获取当前用户
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # 以下是OJT.post()源码中拿user的语句
            user = serializer.object.get('user') or request.user
            # 合并购物车删除cookie中的cart
            response = merge_cart_cookie_to_redis(request, user, response)
        return response




