# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-6-28 上午10:33
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django_redis import get_redis_connection

from .utils import AuthQQ
from users.models import User
from .models import OAuthQQUser


class OAuthQQUserSerializer(serializers.Serializer):
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', write_only=True, min_length=8, max_length=20)
    sms_code = serializers.CharField(label='短信验证码', min_length=6, max_length=6)
    access_token = serializers.CharField(label='操作凭证')

    # 验证手机号是否存在，存在则验证密码，短信验证码，和access_token并绑定
    # 不存在则，验证短信验证码，access_token,创建新账号并绑定
    def validate(self, attrs):
        # 验证access_token
        access_token = attrs.get('access_token')
        openid = AuthQQ.check_save_user_token(access_token)
        if openid is None:
            raise ValidationError('错误的access_token')
        attrs['openid'] = openid

        # 验证短信验证码
        mobile = attrs.get('mobile')
        sms_code = attrs.get('sms_code')
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % mobile).decode()
        if real_sms_code is None:
            raise ValidationError('无效的短信验证码')
        if real_sms_code != sms_code:
            raise ValidationError('错误的短信验证码')

        # 验证手机号是否存在,如果存在验证用户密码
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            pass
        else:
            password = attrs.get('password')
            if not user.check_password(password):
                raise ValidationError('用户密码错误')
            attrs['user'] = user
        return attrs

    # 在OAuthQQUser中创建用户绑定本网站的用户

    def create(self, validated_data):
        user = validated_data.get('user')
        if not user:
            user = User.objects.cerate_user(
                username=validated_data['mobile'],
                mobile=validated_data['mobile'],
                password=validated_data['password']
            )
            user.save()
        # 绑定
        OAuthQQUser.objects.create(
            user=user,
            openid=validated_data['openid']
        )
        return user  # 当调用serializer.save()时，会调用序列化器的create，update等方法，所以可以通过返回user的方式将user传到视图中