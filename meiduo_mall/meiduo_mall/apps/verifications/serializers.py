# !/usr/bin/env python
# _*_ coding:utf-8 _*_
# author: zero
# datetime:18-6-20 下午4:26
from redis.exceptions import RedisError
from rest_framework import serializers
from django_redis import get_redis_connection

import logging

# 获取在配置文件中定义的logger，用来记录日志
logger = logging.getLogger('meiduo')


# 定义图片验证码序列化器，用于验证前端传过来的图片验证码
class ImageCodeSerializer(serializers.Serializer):
    image_code_id = serializers.UUIDField()
    image_code = serializers.CharField(max_length=4, min_length=4)

    def validate(self, attrs):
        image_code = attrs['image_code']
        image_code_id = attrs['image_code_id']

        # 获取数据库中的text
        redis_conn = get_redis_connection('verify_codes')
        text = redis_conn.get('img_%s' % image_code_id)

        # 判断图片id是否在redis中
        if text is None:
            raise serializers.ValidationError('图片验证码无效')

        # 删除图片验证码并记录日志信息
        try:
            redis_conn.delete('img_%s' % image_code_id)
        except RedisError as e:
            logger.error(e)

        # 解码从redis中获取到的验证码，并校验
        text = text.decode()
        if text.lower() != image_code.lower():
            raise serializers.ValidationError('图片验证码错误')

        # 验证有没有在60s内给该手机号发送短信
        # 利用序列化器中封装的上下文对象来获取视图中的参数
        mobile = self.context['view'].kwargs['mobile']
        is_send = redis_conn.get('send_flag_%s' % mobile)

        if is_send:
            raise serializers.ValidationError('短信发送过于频繁')

        # 返回attrs
        return attrs