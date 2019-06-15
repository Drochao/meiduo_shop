import re

from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from users import constants
from django.contrib.auth.backends import ModelBackend

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
