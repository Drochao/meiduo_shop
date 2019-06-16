from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData

from users.models import User
from verifications import constants


def check_verify_email_token(token):
    """验证token并提取user"""
    serializer = Serializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    try:
        data = serializer.loads(token)
    except BadData:
        return None
    else:
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user
