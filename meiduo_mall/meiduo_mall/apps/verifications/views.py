from django.http.response import HttpResponse
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from django_redis import get_redis_connection
import random
from rest_framework.response import Response
from rest_framework import status

# 自己定义的模块
from . import serializers
from . import constants
from celery_tasks.sms.tasks import send_sms_code


# 第三方包
from meiduo_mall.libs.captcha.captcha import captcha
# from meiduo_mall.libs.yuntongxun.sms import CCP


class ImageCodeView(APIView):
    def get(self, request, image_code_id):
        # 1.生成图片验证码
        text, image = captcha.generate_captcha()
        # 2.缓存
        # 2.1 创建redis操作对象
        redis_conn = get_redis_connection("verify_codes")
        # 2.2 保存图片验证码 setex<'键', '有效时间', '值'>
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        # 3.返回图片验证码
        return HttpResponse(image, content_type="images/jpg")


class SmsCodeView(GenericAPIView):
    # 导入序列化器,校验图片验证码
    serializer_class = serializers.ImageCodeSerializer

    def get(self, request, mobile):
        # 验证图片验证码
        serializer = self.get_serializer(data=request.query_params)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            print(e)

        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)

        # 保存短信验证码,和发送短信标示
        redis_conn = get_redis_connection("verify_codes")
        pl = redis_conn.pipeline()  # 获取管道对象，类似与mysql中的事务处理translate,将两次数据库合成一次，提高性能
        pl.multi()
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()

        # # 发送短信验证码, 功能已实现，生产环境可使用
        # ccp = CCP()
        # interval = constants.SEND_SMS_CODE_INTERVAL/60
        # # 注意： 测试的短信模板编号为1
        # ccp.send_template_sms(mobile, [sms_code, interval], constants.SMS_TEMP_ID)

        # 调用celery_tasks中任务模块中的任务代码
        # send_sms_code.delay(mobile, sms_code)
        print('*'*20,'短信验证码', sms_code)

        # 返回响应状态
        return Response({"message": "OK"}, status.HTTP_200_OK)


# 验证access_token发送短信
class SMSCodeByTokenView(GenericAPIView):
    serializer_class = serializers.CheckAccessTokenForSMSSerializer

    def get(self, request):
        # 验证access_token并且60秒内未发送过短信
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.mobile
        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)

        # 保存短信验证码,和发送短信标示
        redis_conn = get_redis_connection("verify_codes")
        pl = redis_conn.pipeline()  # 获取管道对象，类似与mysql中的事务处理translate,将两次数据库合成一次，提高性能
        pl.multi()
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.execute()

        # 调用celery_tasks中任务模块中的任务代码,发送短信
        # send_sms_code.delay(mobile, sms_code)
        print(sms_code)
        # 返回200 ok
        return Response(data={'message':'ok'}, status=status.HTTP_200_OK)


