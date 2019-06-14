import json
import logging
import re

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from celery_tasks.email.tasks import send_verify_email
from meiduo_mall.settings import dev
from meiduo_mall.utils.response_code import RETCODE
from users.models import User
from users.utils import UsernameMobileAuthBackend


logger = logging.getLogger('user')
class RegisterView(View):
    """注册类视图"""

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        sms_code = request.POST.get('sms_code')
        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow]):
            return HttpResponseForbidden('缺少必传参数')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[\da-zA-Z_-]{5,20}$', username):
            return HttpResponseForbidden('请输入5-20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[\d]{8,20}$', password):
            return HttpResponseForbidden('请输入8-20个数字的密码')
        # 判断两次密码是否一致
        if password != password2:
            return HttpResponseForbidden('两次输入的密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('两次输入的密码不一致')
        # 判断是否勾选用户协议
        if allow != 'on':
            return HttpResponseForbidden('请勾选用户协议')

        # 判断短信验证码是否正确
        redis_conn = get_redis_connection('verify_code')

        sms_code_server = redis_conn.get(f'sms_{mobile}')
        if sms_code_server is None:
            return HttpResponseForbidden('短信验证码已经过期')
        redis_conn.delete(f'sms_{mobile}')

        sms_code_server = sms_code_server.decode()

        if sms_code != sms_code_server:
            return HttpResponseForbidden("手机验证码输入有误!!")

        # 保存注册数据
        try:
            user = User.objects.create_user(username=username, password=password,
                                            mobile=mobile)
        except Exception as e:
            print(e)
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        login(request, user)
        # 响应注册结果
        response = redirect(reverse('contents:index'))

        # 注册时用户名写入到cookie，有效期15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 14)

        return response


class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, username):
        count = User.objects.filter(username=username).count()
        content = {
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'count': count,
        }
        return JsonResponse(content)


class MobileCountView(View):
    """判断用户名是否重复注册"""

    def get(self, mobile):
        count = User.objects.filter(mobile=mobile).count()
        content = {
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'count': count,
        }
        return JsonResponse(content)


class LoginView(View):
    """用户登录"""

    def get(self, request):
        """展示登录页面"""
        return render(request, 'login.html')

    def post(self, request):
        """实现用户登录"""
        # 获取数据
        username = request.POST.get("username")
        password = request.POST.get("password")
        remembered = request.POST.get("remembered")
        # 校验数据
        user = UsernameMobileAuthBackend()

        user = user.authenticate(request, username=username, password=password)
        if not user:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})
        # 状态保持
        login(request, user)

        if remembered != "on":
            request.session.set_expiry(0)

        # 响应登录结果
        response = redirect(request.GET.get('next', '/'))

        # 登录时用户名写入到cookie，有效期15天
        response.set_cookie('username', user.username, max_age=(
            None if not remembered else settings.SESSION_COOKIE_AGE))

        return response


class LogoutView(View):
    """退出登录"""

    def get(self, request):
        """实现退出登陆逻辑"""
        logout(request)

        response = redirect(reverse('users:login'))

        response.delete_cookie('username')

        return response


class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""

    # @method_decorator(login_required)
    # def get(self, request):
    #     """提供个人信息界面"""
    #     # 源码的方法，实际采用装饰器方法
    #     # if request.user.is_authenticated:  # 这里返回的不是bool值，不能用布尔值去比较
    #     #     return render(request, 'user_center_info.html')
    #     # else:
    #     #     return redirect(reverse('users:login') + '/?next=/info/')
    #     return render(request, 'user_center_info.html')

    def get(self, request):
        context = {
            'username': request.user.username,
            'mobile': request.user.username,
            'email': request.user.username,
            'email_active': request.user.username,
        }
        return render(request, 'user_center_info.html', context=context)


class EmailView(LoginRequiredMixin, View):
    """添加邮箱"""
    def put(self, request):
        """实现添加邮箱逻辑"""
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')

        if not email:
            return JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少email参数'})

        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return JsonResponse({'code': RETCODE.EMAILERR, 'errmsg': '邮箱格式错误'})

        user = request.user

        User.objects.filter(username=user.username, email='').update(email=email)
        try:
            user.email = email
            user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})

        verify_url = '邮件验证链接'
        send_verify_email.delay(email, verify_url)

        return JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})
