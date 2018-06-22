from celery_tasks.main import app
from .yuntongxun.sms import CCP
from . import constants


# task()中可以填写 任务名称，如果不填，则把当前任务作为 任务名称
@app.task(name="send_sms_code")
def send_sms_code(mobile, sms_code):
    """
    发送短信的异步任务
    :param mobile: 手机号
    :param sms_code: 短信验证码
    :return: None
    """
    ccp = CCP()
    time = str(constants.SMS_CODE_REDIS_EXPIRES / 60)
    ccp.send_template_sms(mobile, [sms_code, time], constants.SMS_TEMP_ID)