from django.contrib.auth.models import AbstractUser
from django.db import models

from itsdangerous import TimedJSONWebSignatureSerializer as TJWSerializer, BadData
from django.conf import settings
from . import constants


class User(AbstractUser):
    """用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(verbose_name='邮箱验证状态', default=False)

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name  # 复数名

    # 生成itsdangerous的access_token
    def generate_sms_code_token(self):
        """生成发送短信的临时票据[access_token]"""
        # TJWSerializer(秘钥,token有效期[秒])
        serializer = TJWSerializer(settings.SECRET_KEY, constants.SMS_CODE_TOKEN_EXPIRES)
        # serializer.dumps(数据), 返回bytes类型
        token = serializer.dumps({'mobile': self.mobile})
        # 把bytes转成字符串
        token = token.decode()
        return token

    # 验证发送短信验证码所需要的access_token
    @staticmethod
    def check_sms_code_token(access_token):
        # 生成操作access_token的serializer对象
        serializer = TJWSerializer(settings.SECRET_KEY, constants.SMS_CODE_TOKEN_EXPIRES)
        # serializer.loads(数据), 返回字典类型
        data = serializer.loads(access_token)
        return data['mobile']

    def generate_password_token(self):
        """生成重置密码所需要的access_token"""
        serializer = TJWSerializer(settings.SECRET_KEY, constants.SMS_CODE_TOKEN_EXPIRES)
        # serializer.dumps(数据), 返回bytes类型
        token = serializer.dumps({'user_id': self.id})
        # 把bytes转成字符串
        token = token.decode()
        return token

    @staticmethod
    def check_password_token(access_token, user_id):
        """验证重置密码所需要的access_token"""
        serializer = TJWSerializer(settings.SECRET_KEY, constants.SMS_CODE_TOKEN_EXPIRES)
        # serializer.loads(数据), 返回字典类型
        try:
            data = serializer.loads(access_token)
        except BadData:
            return False
        else:
            if user_id == str(data.get('user_id')):
                return True
            else:
                return False

    def generate_verify_email_url(self):
        """通过id, email生成access_token，拼接验证邮箱的地址"""
        serializer = TJWSerializer(settings.SECRET_KEY, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        data = {'email':self.email, 'user_id':self.id}
        token = serializer.dumps(data)
        # 把bytes转成字符串
        token = token.decode()
        # 拼接验证地址
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token
        return verify_url

    @staticmethod
    def verify_email_token(access_token):
        serializer = TJWSerializer(settings.SECRET_KEY, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        try:
            data = serializer.loads(access_token)
        except BadData:
            return None
        else:
            email = data.get('email')
            user_id = data.get('user_id')
            try:
                user = User.objects.get(id=user_id, email=email)
            except User.DoesNotExist:
                return None
            else:
                return user