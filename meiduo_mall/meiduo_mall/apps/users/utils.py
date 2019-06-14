import re

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
