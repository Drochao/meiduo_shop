import random
from venv import logger

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render


# Create your views here.
from django.views import View
from django_redis import get_redis_connection
from qcloudsms_py import SmsSingleSender
from qcloudsms_py.httpclient import HTTPError

from meiduo_mall.libs.captcha.captcha import captcha
from meiduo_mall.utils.response_code import RETCODE
from verifications import constants


class ImageCodeView(View):
    """图形验证码"""
    def get(self, request, uuid):
        # 生成图形验证码
        name, text, image = captcha.generate_captcha()
        # 创建redis连接对象
        redis_conn = get_redis_connection('image_code')
        # 将图形
        redis_conn.setex(uuid, constants.IMAGE_CODE_EXPIRES, text)

        return HttpResponse(image, content_type='image/jpg')


class SMSCodeView(View):
    """短信验证码"""
    def get(self, request, mobile):
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        if not all([image_code_client, uuid]):
            return JsonResponse({
                'code': RETCODE.NECESSARYPARAMERR,
                'errmsg': '缺少必传参数'})

        redis_conn = get_redis_connection('image_code')

        image_code_server = redis_conn.get(uuid)
        if image_code_server is None:
            return JsonResponse({
                'code': RETCODE.IMAGECODEERR,
                'errmsg': '图形验证码失效'
            })

        redis_conn.delete(uuid)

        image_code_server = image_code_server.decode()
        if image_code_client.lower() != image_code_server.lower():
            return JsonResponse({
                'code': RETCODE.IMAGECODEERR,
                'errmsg': '输入图形验证码有误'
            })

        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)

        redis_conn.setex(f'sms_{mobile}', constants.SMS_CODE_REDIS_EXPIRES, sms_code)

        result = q_sms(mobile, sms_code)
        if result:
            return JsonResponse({
                'code': RETCODE.OK,
                'errmsg': '发送短信成功'
            })
        else:
            return JsonResponse({
                'code': RETCODE.MOBILEERR,
                'errmsg': '发送短信失败'
            })


def q_sms(mobile, sms_code):
    """发送短信"""
    appid = 1400219871  # SDK AppID

    # 短信应用 SDK AppKey
    appkey = "7358ac75a7c5db705d051ac458e345be"

    # 短信模板ID
    template_id = 349902

    # 签名
    sms_sign = "醉生梦死着公众号"

    ssender = SmsSingleSender(appid, appkey)
    params = [sms_code, "1"]  # 当模板没有参数时，`params = []`

    result = ssender.send_with_param(86, mobile,template_id, params, sign=sms_sign, extend="", ext="")
    if result['errmsg'] == 'OK':
        return 1
    else:
        return 0
