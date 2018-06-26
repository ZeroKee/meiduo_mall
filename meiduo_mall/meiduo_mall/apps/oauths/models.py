from django.db import models

from meiduo_mall.utils.models import BaseModel


class OAuthQQUser(BaseModel):
    """QQ登陆用户数据"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    openid = models.CharField(verbose_name='QQ登陆用户在网站中的唯一标示', max_length=64, db_index=True)

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登陆用户表'
        verbose_name_plural = verbose_name
