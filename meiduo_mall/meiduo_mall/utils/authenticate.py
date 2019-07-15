from django.contrib.auth.backends import ModelBackend

from users.models import User


class MeiduoModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 判断是否通过vue组件发送请求
        if request is None:
            try:
                user = User.objects.get(username=username, is_staff=True)
            except:
                return None

            if user.check_password(password):
                return user

        else:
            try:
                user = User.objects.get(username=username)
            except:
                return None

        if user.check_password(password):
            return user
        else:
            return None
