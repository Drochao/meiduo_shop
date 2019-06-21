from celery_tasks.sms.qcloudsms import constants
from celery_tasks.sms.qcloudsms_py.qcloudsms_py.sms import SmsSingleSender

# SDK appId
_appId = 1400219871

# 短信应用 SDK AppKey
_appKey = "7358ac75a7c5db705d051ac458e345be"

# 短信模板ID
_template_id = 349902

# 签名
_sms_sign = "醉生梦死着公众号"


class CCP:
    def __new__(cls, *args, **kwargs):
        if not hasattr(CCP, "_instance"):
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)
            cls._instance.rest = SmsSingleSender(_appId, _appKey)
        return cls._instance

    def send_template_sms(self, to, datas):
        """发送模板短信"""
        # 模板参数
        params = [datas, constants.SMS_CODE_REDIS_EXPIRES // 60]
        # 发送短信
        result = self.rest.send_with_param(86, to, _template_id, params, sign=_sms_sign, extend="", ext="")
        # 如果发送短信成功，返回OK
        if result['errmsg'] == 'OK':
            # 返回0 表示发送短信成功
            return 0
        else:
            # 返回-1 表示发送失败
            return -1
