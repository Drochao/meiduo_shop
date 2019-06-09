import re

from django.contrib.auth import login
from django.db import DatabaseError
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View

from users.models import User


class Register(View):
    """注册类视图"""

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
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

        # 保存注册数据
        try:
            user = User.objects.create_user(username=username, password=password,
                                            mobile=mobile)
        except Exception as e:
            print(e)
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        login(request, user)

        return redirect(reverse('contents:index'))
