# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-6-22 上午9:44
from rest_framework import serializers
import re
from django.core.exceptions import ValidationError
from django_redis import get_redis_connection
from rest_framework_jwt.settings import api_settings

from .models import User
from .utils import get_user_by_account


class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label='确认密码', required=True, allow_null=False, allow_blank=False, write_only=True)
    sms_code = serializers.CharField(label='短信验证码', required=True, allow_blank=False, allow_null=False, write_only=True)
    allow = serializers.CharField(label='同意协议', required=True, allow_blank=False, allow_null=False, write_only=True)
    token = serializers.CharField(label='登陆状态token', read_only=True)

    def validate_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            # print('手机号不符')
            raise ValidationError('手机号格式不符')
        return value

    def validate_allow(self, value):
        """检查用户同意协议"""
        if value != 'true':
            # print('用户协议没点')
            raise ValidationError('请同意用户协议')
        return value

    def validate(self, attrs):
        mobile = attrs['mobile']
        sms_code = attrs['sms_code']
        password = attrs['password']
        password2 = attrs['password2']
        # print(attrs)

        # 判断两次验证码是否一致
        if password != password2:
            # print('密码不一致')
            raise ValidationError('两次密码需一致')

        # 判断短信验证码是否正确
        redis_conn = get_redis_connection('verify_codes')
        # redis中查询到的数据是bytes类型，需要转码
        real_sms_code = redis_conn.get('sms_%s' % mobile).decode()
        print(real_sms_code)
        if real_sms_code is None:
            # print('短信验证码无效')
            raise ValidationError('无效的短信验证码')
        if real_sms_code != sms_code:
            # print('短信验证码错误')
            raise ValidationError('短信验证码错误')
        return attrs

    # 创建新用户
    def create(self, validated_data):
        # 删除不需要保存的字段,模型类中不存在的数据
        del validated_data['password2']
        del validated_data['sms_code']
        del validated_data['allow']

        # 创建新用户
        user = super().create(validated_data)
        # user = User.objects.create(**validated_data)

        # 认证密码
        user.set_password(validated_data['password'])
        user.save()

        # 生成token，并保存在user对象中
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        # 生成载荷
        payload = jwt_payload_handler(user)
        # 生成token
        token = jwt_encode_handler(payload)
        user.token = token
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'mobile',
                  'sms_code', 'allow', 'password2', 'token')
        # 添加字段约束
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {'required': True,
                         'max_length': 20,
                         'min_length': 5,
                         'error_messages': {
                             'min_length': '用户名长度为5-20位',
                             'max_length': '用户名长度为5-20位'
                         }
                         },
            'password': {'required': True,
                         'write_only': True,
                         'max_length': 20,
                         'min_length': 8,
                         'error_messages': {
                             'min_length': '用户密码长度为8-20位',
                             'max_length': '用户密码长度为8-20位',
                         }
                         },

        }


# 验证短信验证码
class CheckSMSCodeSerializer(serializers.Serializer):
    sms_code = serializers.CharField(required=True, allow_null=False, allow_blank=False)

    # 验证账户名和短信验证码
    def validate_sms_code(self, value):
        sms_code = value
        # 验证账户
        account = self.context['view'].kwargs['account']
        user = get_user_by_account(account)

        if user is None:
            raise ValidationError('用户名或手机号错误')

        # 验证短信验证码
        mobile = user.mobile
        redis_conn = get_redis_connection('verify_codes')
        # redis中查询到的数据是bytes类型，需要转码
        real_sms_code = redis_conn.get('sms_%s' % mobile).decode()
        print(real_sms_code)
        if real_sms_code is None:
            # print('短信验证码无效')
            raise ValidationError('无效的短信验证码')
        if real_sms_code != sms_code:
            # print('短信验证码错误')
            raise ValidationError('短信验证码错误')

        self.user = user

        return value


# 验证重置密码所需要的access_token，验证确认密码，并修改密码
class CheckPasswordTokenSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label='确认密码', required=True, write_only=True)
    access_token = serializers.CharField(label='重置密码所需的access_token', required=True, write_only=True)

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        access_token = attrs.get('access_token')

        if password != password2:
            raise ValidationError('两次密码不一致')

        user_id = self.context['view'].kwargs.get('pk')

        # 验证access_token中的user_id与url中的pk是否相等
        is_true = User.check_password_token(access_token, user_id)
        if not is_true:
            raise ValidationError('无效的access_token')

        return attrs

    def update(self, instance, validated_data):
        # 设置密码
        instance.set_password(validated_data.get('password'))
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ['id', 'password', 'password2', 'access_token']
        extral_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min': '密码位数为8-20',
                    'max': '密码位数为8-20'
                }
            }
        }
