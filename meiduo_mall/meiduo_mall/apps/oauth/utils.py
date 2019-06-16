from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData

from oauth import constants


def generate_openid_signature(openid):
    """
    签名openid
    :param openid: 用户的openid
    :return: 加密后的id
    """
    serializer = Serializer(settings.SECRET_KEY, expires_in=constants.ACCESS_TOKEN_EXPIRES)
    data = {'openid': openid}
    token = serializer.dumps(data)
    return token.decode()


def check_openid_signature(openid_sign):
    """对openid进行解密，并返回原声openid"""
    # 创建加密对象
    serializer = Serializer(settings.SECRET_KEY, expires_in=constants.ACCESS_TOKEN_EXPIRES)
    try:
        data = serializer.loads(openid_sign)
    except BadData:
        return None
    else:
        return data.get('openid')
