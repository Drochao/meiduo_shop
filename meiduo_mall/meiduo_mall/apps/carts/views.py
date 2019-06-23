import base64
import json
import pickle

from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE


class CartsView(View):
    """购物车管理"""
    def post(self, request):
        """添加购物车"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        if not all([sku_id, count]):
            return HttpResponseForbidden("缺少必传参数")

        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return HttpResponseForbidden('商品不存在')

        try:
            count = int(count)
        except Exception:
            return HttpResponseForbidden('参数count有误')

        if selected:
            if not isinstance(selected, bool):
                return HttpResponseForbidden('参数selected 有误')

        user = request.user
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hincrby(f"carts_{user.id}", sku_id, count)

            if selected:
                pl.sadd(f'selected_{user.id}', sku_id)
            pl.execute()

            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

        else:
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

            if sku_id in cart_dict:
                origin_count = cart_dict[sku_id]['count']
                count += origin_count

            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            cooker_cart_str = base64.b64encode(pickle.dumps(cart_dict).decode())

            response = JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

            return response

    def get(self, request):
        """展示购物车"""
        user = request.user
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')

            redis_cart = redis_conn.hgetall(f'carts_{user.id}')

            cart_selected = redis_conn.smembers(f'selected_{user.id}')

            cart_dict = {}

            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in cart_selected
                }
        else:
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64encode(cart_str.encode()))
            else:
                cart_dict = {}
                return render(request, 'cart.html')

        sku_ids = cart_dict.keys()

        skus = SKU.objects.filter(id__in=sku_ids)

        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'selected': str(cart_dict.get(sku.id).get('selected')),
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),
                'amount': str(sku.price * cart_dict.get(sku.id).get('count'))
            })

        context = {
            'cart_skus': cart_skus
        }

        return render(request, 'cart.html', context)