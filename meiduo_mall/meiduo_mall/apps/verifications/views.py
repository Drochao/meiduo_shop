import base64
import json
import logging
import pickle
import random
import re

from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseServerError
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from celery_tasks.sms.tasks import send_sms_code
from meiduo_mall.libs.captcha.captcha import captcha
from meiduo_mall.utils.response_code import RETCODE
from users.models import User
from verifications import constants
from verifications.utils import check_verify_email_token

logger = logging.getLogger('django')


class ImageCodeView(View):
    """图形验证码"""

    def get(self, request, uuid):
        # 生成图形验证码
        name, text, image = captcha.generate_captcha()
        # 创建redis连接对象
        redis_conn = get_redis_connection('verify_code')
        # 将图形验证码的字符 存储到redis中 用uuid作为key
        redis_conn.setex(uuid, constants.IMAGE_CODE_EXPIRES, text)
        print(text)

        return HttpResponse(image, content_type='image/jpg')


class SMSCodeView(View):
    """短信验证码"""

    def get(self, request, mobile):
        # 0 创建redis连接对象
        redis_conn = get_redis_connection('verify_code')
        send_flag = redis_conn.get(f'flag_{mobile}')
        if send_flag:
            return JsonResponse({
                'code': RETCODE.NECESSARYPARAMERR,
                'errmsg': '频繁发送短信'
            })
        # 1 接受前端传入的数据
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        # 2 校验数据
        if not all([image_code_client, uuid]):
            return JsonResponse({
                'code': RETCODE.NECESSARYPARAMERR,
                'errmsg': '缺少必传参数'})

        # 2.2 获取redis的图形验证码
        image_code_server = redis_conn.get(uuid)
        # 2.3 判断图形验证码是否为空
        if image_code_server is None:
            return JsonResponse({
                'code': RETCODE.IMAGECODEERR,
                'errmsg': '图形验证码失效'
            })
        # 2.4 图形验证码只能使用一次，提高安全性
        redis_conn.delete(uuid)
        # 2.5 已经保证图形验证码不为空，解码
        image_code_server = image_code_server.decode()
        # 2.6 判断用户输入验证码是否正确 注意转换大小写
        if image_code_client.lower() != image_code_server.lower():
            return JsonResponse({
                'code': RETCODE.IMAGECODEERR,
                'errmsg': '输入图形验证码有误'
            })
        # 3 随机生成一个6位数字作为验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)

        # redis管道技术
        pl = redis_conn.pipeline()

        # redis_conn.setex(f'sms_{mobile}', constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex(f'sms_{mobile}', constants.SMS_CODE_REDIS_EXPIRES, sms_code)

        pl.setex(f'flag_{mobile}', constants.SMS_CODE_REDIS_EXPIRES, 1)

        # 执行管道
        pl.execute()

        # 生产任务
        send_sms_code.delay(mobile, sms_code)
        return JsonResponse({
            'code': RETCODE.OK,
            'errmsg': '发送短信验证码成功'
        })


class VerifyEmailView(View):
    """验证邮箱"""

    def get(self, request):
        """实现邮箱验证逻辑"""
        token = request.GET.get('token')

        if not token:
            return HttpResponseBadRequest('缺少token')

        user = check_verify_email_token(token)
        if not user:
            return HttpResponseForbidden('无效的token')

        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return HttpResponseServerError('激活邮件失败')
        # 什么时候显示已验证
        return redirect(reverse('users:info'))


class VerifyUserView(View):
    def get(self, request, username):
        # 0 创建redis连接对象
        redis_conn = get_redis_connection('verify_code')
        # 1 接受前端传入的数据
        image_code_client = request.GET.get('text')
        uuid = request.GET.get('image_code_id')

        # 2 校验数据
        if not all([image_code_client, uuid]):
            return JsonResponse({
                'code': RETCODE.NECESSARYPARAMERR,
                'errmsg': '缺少必传参数'})

        # 2.2 获取redis的图形验证码
        image_code_server = redis_conn.get(uuid)
        # 2.3 判断图形验证码是否为空
        if image_code_server is None:
            return JsonResponse({
                'code': RETCODE.IMAGECODEERR,
                'errmsg': '图形验证码失效'
            })
        # 2.4 图形验证码只能使用一次，提高安全性
        redis_conn.delete(uuid)
        # 2.5 已经保证图形验证码不为空，解码
        image_code_server = image_code_server.decode()
        # 2.6 判断用户输入验证码是否正确 注意转换大小写
        if image_code_client.lower() != image_code_server.lower():
            return JsonResponse({
                'code': RETCODE.IMAGECODEERR,
                'errmsg': '输入图形验证码有误'
            })
        user_query = User.objects.get(username=username)
        mobile = user_query.mobile
        user_dict = {
            'username': username,
            'mobile': mobile
        }
        access_token = base64.b64encode(pickle.dumps(user_dict)).decode()
        return JsonResponse({
            'mobile': mobile,
            'access_token': access_token
        })


class SMSVerifyView(View):
    """短信验证码"""

    def get(self, request):
        access_token = request.GET.get('access_token')
        user_dict = pickle.loads(base64.b64decode(access_token.encode()))
        mobile = user_dict['mobile']
        # 0 创建redis连接对象
        redis_conn = get_redis_connection('verify_code')
        # send_flag = redis_conn.get(f'flag_{mobile}')
        # if send_flag:
        #     return JsonResponse({
        #         'code': RETCODE.NECESSARYPARAMERR,
        #         'errmsg': '频繁发送短信'
        #     })

        # 3 随机生成一个6位数字作为验证码
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)
        # redis管道技术
        pl = redis_conn.pipeline()

        # redis_conn.setex(f'sms_{mobile}', constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex(f'sms_{mobile}', constants.SMS_CODE_REDIS_EXPIRES, sms_code)

        # pl.setex(f'flag_{mobile}', constants.SMS_CODE_REDIS_EXPIRES, 1)

        # 执行管道
        pl.execute()

        # 生产任务
        send_sms_code.delay(mobile, sms_code)
        return JsonResponse({
            'code': RETCODE.OK,
            'errmsg': '发送短信验证码成功'
        })


class VerifyPasswordView(View):
    def get(self, request, username):
        user = User.objects.get(username=username)

        mobile = user.mobile
        # 判断短信验证码是否正确
        redis_conn = get_redis_connection('verify_code')

        sms_code_server = redis_conn.get(f'sms_{mobile}')
        if sms_code_server is None:
            return HttpResponseForbidden('短信验证码已经过期')
        redis_conn.delete(f'sms_{mobile}')

        sms_code_server = sms_code_server.decode()
        sms_code_client = request.GET.get('sms_code')
        if sms_code_client != sms_code_server:
            return HttpResponseForbidden("手机验证码输入有误!!")

        user_dict = {
            username: username,
            'user_id': user.id
        }
        access_token = base64.b64encode(pickle.dumps(user_dict)).decode()
        return JsonResponse({
            'user_id': user.id,
            'access_token': access_token
        })


class ResetPassword(View):
    def post(self, request, user_id):
        # 获取请求参数：
        json_dict = json.loads(request.body.decode())
        pwd = json_dict.get('password')
        pwd2 = json_dict.get('password2')
        access_token = json_dict.get('access_token')

        # 校验数据
        # 判断参数是否齐全
        if not all([pwd, pwd2, access_token]):
            return HttpResponseForbidden('缺少必传参数')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[a-zA-Z\d]{8,20}$', pwd):
            return HttpResponseForbidden('请输入8-20个数字的密码')
        # 判断两次密码是否一致
        if pwd != pwd2:
            return HttpResponseForbidden('两次输入的密码不一致')

        user_dict = pickle.loads(base64.b64decode(access_token.encode()))
        if user_id != user_dict['user_id']:
            return JsonResponse({
                'error': '数据错误',
                'status': 400
            })

        user = User.objects.get(id=user_id)
        user.set_password(pwd)
        user.save()

        return JsonResponse({
            'message': 'ok'
        })