import json
import logging
import random
import re

from django.conf import settings
from django.contrib.auth import login, logout
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from carts.utils import merge_cart_cookie_to_redis
from celery_tasks.email.tasks import send_verify_email
from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredView
from users import constants
from users.models import User, Address
from users.utils import UsernameMobileAuthBackend, generate_verify_email_url, getdata, forbidden
from wallet.models import Wallet

logger = logging.getLogger('user')
OK = {'code': RETCODE.OK, 'errmsg': 'OK'}


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
        if not all([username, password, password2, mobile, allow, sms_code]):
            return HttpResponseForbidden('缺少必传参数')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[\da-zA-Z_-]{5,20}$', username):
            return HttpResponseForbidden('请输入5-20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[a-zA-Z\d]{8,20}$', password):
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

        share_code = '%06d' % random.randint(0, 999999)
        logger.info(share_code)
        try:
            user = Wallet.objects.create(user=user,share_code=share_code, balance=100)
        except Exception as e:
            print(e)
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        login(request, user)
        # 响应注册结果
        response = redirect(reverse('contents:index'))

        # 注册时用户名写入到cookie，有效期15天
        response.set_cookie('username', user.username, max_age=3600 * 24 * 14)

        return response


class FindPasswordView(View):
    def get(self, request):
        return render(request, 'find_password.html')


class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        OK['count'] = count
        return JsonResponse(OK)


class MobileCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        OK['count'] = count
        return JsonResponse(OK)


class LoginView(View):
    """用户登录"""

    def get(self, request):
        """展示登录页面"""
        return render(request, 'login.html', context={'title': '登录'})

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

        merge_cart_cookie_to_redis(request, response)

        return response


class LogoutView(View):
    """退出登录"""

    def get(self, request):
        """实现退出登陆逻辑"""
        logout(request)

        response = redirect(reverse('users:login'))

        response.delete_cookie('username')

        return response


class UserInfoView(LoginRequiredView):
    """用户中心"""

    def get(self, request):
        context = {
            'username': request.user.username,
            'mobile': request.user.username,
            'email': request.user.username,
            'email_active': request.user.username,
        }
        return render(request, 'user_center_info.html', context=context)


class EmailView(LoginRequiredView):
    """添加邮箱"""

    def put(self, request):
        """实现添加邮箱逻辑"""
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')

        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return HttpResponseForbidden('邮箱格式错误')

        user = request.user

        try:
            user.email = email
            user.save()
            # 本来是要更新比较好，但是前端一旦存入数据库直接禁止修改
            # User.objects.filter(username=user.username, email='').update(email=email)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})

        verify_url = generate_verify_email_url(user)
        send_verify_email.delay(email, verify_url)

        return JsonResponse(OK)


class AddressView(LoginRequiredView):
    """用户收货地址"""

    def get(self, request):
        """用户收货地址展示"""
        login_user = request.user
        addresses = Address.objects.filter(user=login_user, is_deleted=False)

        address_dict_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province_id": address.province_id,
                "province": address.province.name,
                "city_id": address.city_id,
                "city": address.city.name,
                "district_id": address.district_id,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)

        context = {
            'default_address_id': login_user.default_address_id,
            'addresses': address_dict_list
        }
        return render(request, 'user_center_site.html', context)


class CreateAddressView(LoginRequiredView):
    """新增地址"""

    def post(self, request):
        """实现新增地址逻辑"""
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '超过地址数量上限'})

        data_list = getdata(request)

        ret = forbidden(data_list)
        if ret:
            return HttpResponseForbidden(ret)

        try:
            address = Address.objects.create(
                user=request.user,
                title=data_list[0],
                receiver=data_list[0],
                province_id=data_list[1],
                city_id=data_list[2],
                district_id=data_list[3],
                place=data_list[4],
                mobile=data_list[5],
                tel=data_list[6],
                email=data_list[7])
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            'province_id': address.province_id,
            "province": address.province.name,
            'city_id': address.city_id,
            "city": address.city.name,
            'district_id': address.district_id,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email,
        }
        OK['address'] = address_dict
        return JsonResponse(OK)


class UpdateDestroyAddressView(LoginRequiredView):
    """修改和删除地址"""

    def put(self, request, address_id):
        """修改地址"""
        data_list = getdata(request)

        ret = forbidden(data_list)
        if ret:
            return HttpResponseForbidden(ret)

        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=data_list[0],
                receiver=data_list[0],
                province_id=data_list[1],
                city_id=data_list[2],
                district_id=data_list[3],
                place=data_list[4],
                mobile=data_list[5],
                tel=data_list[6],
                email=data_list[7])
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '更新地址失败'})

        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        OK['address'] = address_dict
        return JsonResponse(OK)

    def delete(self, request, address_id):
        """删除地址"""
        try:
            address = Address.objects.get(id=address_id)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})

        address.is_deleted = True
        address.save()
        return JsonResponse(OK)


class DefaultAddressView(LoginRequiredView):
    """设置默认地址"""

    def put(self, request, address_id):
        """设置默认地址"""
        try:
            address = Address.objects.get(id=address_id)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置默认地址失败'})

        request.user.default_address = address
        request.user.save()
        return JsonResponse(OK)


class UpdateTitleAddressView(LoginRequiredView):
    """设置地址标题"""

    def put(self, request, address_id):
        """设置地址标题"""
        # 获取请求数据
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')

        try:
            address = Address.objects.get(id=address_id)

        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置地址标题失败'})

        address.title = title
        address.save()
        return JsonResponse(OK)


class ChangePasswordView(LoginRequiredView):
    """修改密码"""

    def get(self, request):
        """展示修改密码界面"""
        return render(request, 'user_center_pass.html')

    def post(self, request):
        """实现修改密码逻辑"""
        old_pwd = request.POST.get('old_pwd')
        new_pwd = request.POST.get('new_pwd')
        new_pwd2 = request.POST.get('new_cpwd')

        user = request.user
        if not all([old_pwd, new_pwd, new_pwd2]):
            return HttpResponseForbidden('缺少必传参数')
        # 用False性能更高
        if user.check_password(old_pwd) is False:
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg': '原始密码错误'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_pwd):
            return HttpResponseForbidden('密码最少8位，最长20位')
        if new_pwd != new_pwd2:
            return HttpResponseForbidden('两次输入的密码不一致')
        if old_pwd == new_pwd:
            return HttpResponseForbidden('不能设置相同的密码')

        try:
            user.set_password(new_pwd)
            user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '设置密码失败'})

        logout(request)
        response = redirect(reverse('users:login'))
        response.delete_cookie('username')

        return response
        # return redirect(reverse('users:logout'))


class UserBrowseHistory(View):
    """商品浏览记录"""

    def post(self, request):
        if request.user.is_authenticated:
            json_dict = json.loads(request.body.decode())
            sku_id = json_dict.get('sku_id')

            try:
                sku = SKU.objects.get(id=sku_id)
            except SKU.DoesNotExist:
                return HttpResponseForbidden('sku_id不存在')

            redis_conn = get_redis_connection('history')
            pl = redis_conn.pipeline()

            user = request.user
            key = 'history_%s' % user.id

            pl.lrem(key, 0, sku_id)

            pl.lpush(key, sku_id)

            pl.ltrim(key, 0, 4)

            pl.execute()

            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
        else:
            return JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': '用户未登录'})

    def get(self, request):
        """查询商品浏览记录"""
        if request.user.is_authenticated:
            redis_conn = get_redis_connection('history')
            sku_ids = redis_conn.lrange('history_%s' % request.user.id, 0, -1)

            sku_list = []
            for sku_id in sku_ids:
                sku = SKU.objects.get(id=sku_id)
                sku_list.append({
                    'id': sku.id,
                    'name': sku.name,
                    'default_image_url': sku.default_image.url,
                    'price': sku.price
                })
            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'skus': sku_list})
        else:
            return JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': '用户未登录', 'skus': []})


