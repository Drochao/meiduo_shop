import logging
import re

from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.contrib.auth import login
from django.db import DatabaseError
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import redirect, render
from django.views import View
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE
from oauth import constants
from oauth.models import OAuthQQUser
from oauth.utils import check_openid_signature, generate_openid_signature
from users.models import User

logger = logging.getLogger('django')


class QQAuthURLView(View):
    """提供QQ登录url"""

    def get(self, request):
        # next表示进入登陆页面之前的那个页面
        next = request.GET.get('next', '/')
        # 获取QQ登录页面网址
        auth_qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                          client_secret=settings.QQ_CLIENT_SECRET,
                          redirect_uri=settings.QQ_REDIRECT_URI,
                          state=next)

        login_url = auth_qq.get_qq_url()
        return JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'login_url': login_url})


class QQAuthView(View):
    """QQ登录成功后的回调处理"""

    def get(self, request):
        """Oauth2.0认证"""
        # 先获取验证码
        code = request.GET.get('code')
        if code is None:
            return HttpResponseForbidden('缺少code')

        auth_qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                          client_secret=settings.QQ_CLIENT_SECRET,
                          redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            # 使用code向QQ服务器请求access_token
            access_token = auth_qq.get_access_token(code)

            # 即使需要返回结果，此耗时操作必须等
            # 使用access_token向服务器请求openid
            openid = auth_qq.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return HttpResponseServerError('OAuth2.0认证失败')

        try:
            # 获取openid
            oauth_model = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 当该用户名没有绑定时，要吧openid保存起来，隐藏在前端
            # 保存的openid需要加密处理，不然前端代码可以获取openid，不安全
            openid = generate_openid_signature(openid)
            return render(request, 'oauth_callback.html', {'openid': openid})
        else:
            user = oauth_model.user

            login(request, user)
            response = redirect(request.GET.get('state', '/'))
            response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)
            return response

    def post(self, request):
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')
        sms_code_client = request.POST.get('sms_code')
        openid = request.POST.get('openid')

        # 判断参数是否齐全
        if not all([password, mobile, sms_code_client]):
            return HttpResponseForbidden('缺少必传参数')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[\d]{8,20}$', password):
            return HttpResponseForbidden('请输入8-20个数字的密码')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return HttpResponseForbidden('请输入正确的手机号')
        # 判断短信验证码是否正确
        redis_conn = get_redis_connection('verify_code')

        sms_code_server = redis_conn.get(f'sms_{mobile}')
        if sms_code_server is None:
            return HttpResponseForbidden('短信验证码已经过期')

        sms_code_server = sms_code_server.decode()

        if sms_code_client != sms_code_server:
            return HttpResponseForbidden("手机验证码输入有误!!")
        openid = check_openid_signature(openid)
        if not openid:
            return render(request, 'oauth_callback.html', {'openid_errmsg': '无效的openid'})
        # 保存注册数据
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
        else:
            if not user.check_password(password):
                return render(request, 'oauth_callback.html', {'qq_login_errmsg': 'QQ登录失败'})

        # 将用户绑定openid
        try:
            OAuthQQUser.objects.create(openid=openid, user=user)
        except DatabaseError:
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': '无效的openid'})

        # 实现状态保持
        login(request, user)
        # 响应注册结果
        next = request.GET.get('state')
        response = redirect(next)

        # 注册时用户名写入到cookie，有效期15天
        response.set_cookie('username', user.username, max_age=constants.MAX_AGE)

        return response
