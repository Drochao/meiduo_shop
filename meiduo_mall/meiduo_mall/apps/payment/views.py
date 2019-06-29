import os

from alipay import AliPay
from django import http
from django.conf import settings
from django.shortcuts import render
from django.views import View

from meiduo_mall.utils.response_code import RETCODE
from orders.models import OrderInfo
from payment.models import Payment


class PaymentView(View):
    """订单支付功能"""

    def get(self, request, order_id):
        user = request.user
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息错误')

        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type='RSA2',
            debug=settings.ALIPAY_DEBUG
        )

        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject=f"美多商城{order_id}",
            return_url=settings.ALIPAY_RETURN_URL
        )

        alipay_url = settings.ALIPAY_URL + '?' + order_string
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})


class PaymentStatusView(View):
    """保存订单支付结果"""

    def get(self, request):
        query_dict = request.GET
        data = query_dict.dict()

        signature = data.pop('sign')

        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type='RSA2',
            debug=settings.ALIPAY_DEBUG
        )

        success = alipay.verify(data, signature)
        if success:
            order_id = data.get('out_trade_no')
            trade_id = data.get('trade_no')

            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )

            OrderInfo.objects.filter(
                order_id=order_id,
                status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])

            context = {
                'trade_id': trade_id
            }
            return render(request, 'pay_success.html', context)
        else:
            return http.HttpResponseForbidden('非法请求')
