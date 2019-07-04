import base64
import logging
import pickle
import random

from django.shortcuts import render

from meiduo_mall.utils.views import LoginRequiredView
from wallet.models import Wallet

logger = logging.getLogger('meiduo')


class WalletView(LoginRequiredView):
    """钱包系统"""
    def get(self, request):
        context = {
            'title': '钱包'
        }
        return render(request, 'user_center_wallet.html', context)


class ShareView(LoginRequiredView):
    """分享系统"""
    def get(self, request):

        return render(request, 'register2.html')

    # def post(self, request):
    #     access_token = request.GET.get('access_token')
    #     share_code_client = pickle.loads(base64.b64decode(access_token.encode()))
    #
    #     user = request.user
    #     share_code_server = Wallet.objects.get(user=user)
    #     print(share_code_server)



