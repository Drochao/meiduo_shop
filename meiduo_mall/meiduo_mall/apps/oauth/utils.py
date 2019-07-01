import json

import requests
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


class OAuthWB:
    def __init__(self, client_id, client_key, redirect_uri, state=None):
        self.client_id = client_id
        self.client_key = client_key
        self.redirect_uri = redirect_uri
        self.state = state

    def get_access_token(self, code):  # 获取用户token和uid
        url = "https://api.weibo.com/oauth2/access_token"

        querystring = {
            "client_id": self.client_id,
            "client_secret": self.client_key,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }

        response = requests.request("POST", url, params=querystring)

        return json.loads(response.text)

    def get_user_info(self, access_token_data):
        url = "https://api.weibo.com/2/users/show.json"

        querystring = {
            "uid": access_token_data['uid'],
            "access_token": access_token_data['access_token']
        }

        response = requests.request("GET", url, params=querystring)

        return json.loads(response.text)
