import json
import re

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from users import constants
from users.models import User


def get_user_by_account(account):
    """根据account查询用户"""
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """自定义用户认证后端"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """重写认证方法"""
        user = get_user_by_account(username)
        if user and user.check_password(password):
            return user


def generate_verify_email_url(user):
    """生成邮箱验证链接"""
    serializer = Serializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    data = {'user_id': user.id, 'email': user.email}
    token = serializer.dumps(data).decode()
    verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token
    return verify_url


def getdata(req):
    json_dict = json.loads(req.body.decode())
    receiver = json_dict.get('receiver')
    province_id = json_dict.get('province_id')
    city_id = json_dict.get('city_id')
    district_id = json_dict.get('district_id')
    place = json_dict.get('place')
    mobile = json_dict.get('mobile')
    tel = json_dict.get('tel')
    email = json_dict.get('email')
    data_list = [receiver, province_id, city_id, district_id,
                 place, mobile, tel, email]
    return data_list


def forbidden(data_list):
    if not all([data_list[0], data_list[1], data_list[2], data_list[3], data_list[4], data_list[5]]):
        return '缺少必传参数'
    if not re.match(r'^1[3-9]\d{9}$', data_list[5]):
        return '参数mobile有误'
    if data_list[6]:
        if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', data_list[6]):
            return '参数tel有误'
    if data_list[7]:
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', data_list[7]):
            return '参数email有误'


