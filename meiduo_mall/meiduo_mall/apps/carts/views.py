import base64
import json
import pickle

from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from carts import constants
from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE


class CartsView(View):
    """购物车管理"""
    def __init__(self, request, **kwargs):
        super().__init__(**kwargs)
        self.user = request.user

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

        response = JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
        if self.user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hincrby(f"carts_{self.user.id}", sku_id, count)

            if selected:
                pl.sadd(f'selected_{self.user.id}', sku_id)
            pl.execute()

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

            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            response.set_cookie('carts', cookie_cart_str)

        return response

    def get(self, request):
        """展示购物车"""
        if self.user.is_authenticated:
            redis_conn = get_redis_connection('carts')

            redis_cart = redis_conn.hgetall(f'carts_{self.user.id}')

            cart_selected = redis_conn.smembers(f'selected_{self.user.id}')

            cart_dict = {}

            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in cart_selected
                }
        else:
            cart_str = request.COOKIES.get('carts')
            if cart_str:

                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))

            else:
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
    
    def put(self, request):
        """修改购物车"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        if not all([sku_id, count]):
            return HttpResponseForbidden("缺少必传参数")

        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return HttpResponseForbidden('商品不存在')

        try:
            count = int(count)
        except Exception:
            return HttpResponseForbidden('参数count有误')

        if selected:
            if not isinstance(selected, bool):
                return HttpResponseForbidden('参数selected 有误')

        if self.user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hset(f'carts_{self.user.id}', sku_id, count)
            if selected:
                pl.sadd(f'selected_{self.user.id}', sku_id)
            else:
                pl.srem(f'selected_{self.user.id}', sku_id)
            pl.execute()

            cart_sku = {
                'id': sku_id,
                'name': sku.name,
                'count': count,
                'selected': selected,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count
            }
            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_sku': cart_sku})
        else:
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'cookie数据没有获取到'})

            if sku_id in cart_dict:
                origin_count = cart_dict[sku_id]['count']
                count += origin_count

            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            cooker_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count,
            }

            response = JsonResponse({'code':RETCODE.OK, 'errmsg': 'OK', 'cart_sku': cart_sku})

            response.set_cookie('carts', cooker_cart_str, max_age=constants.CARTS_COOKIE_EXPIRES)

            return response

    def delete(self, request):
        """删除购物车"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        try:
            SKU.objects.get(id=sku_id)
        except:
            return HttpResponseForbidden('商品不存在')

        if self.user is not None and self.user.is_authenticated:
            redis_conn = get_redis_connection('carts')

            pl = redis_conn.pipeline()
            pl.hdel(f'carts_{self.user.id}', sku_id)
            pl.srem(f'selected_{self.user.id}', sku_id)
            pl.execute()

            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

        else:
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'cookie数据没获取到'})

            if sku_id in cart_dict:
                del cart_dict[sku_id]

            response = JsonResponse({'code': RETCODE.OK, 'errmsg': "OK"})

            if not cart_dict:
                response.delete_cookie('carts')
                return response

            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            response.set_cookie('carts', cart_str)

            return response


class CartsSelectAllView(View):
    """全选购物车"""
    def put(self, request):
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected', True)

        if selected:
            if not isinstance(selected, bool):
                return HttpResponseForbidden('参数selected有误')

        if self.user is not None and self.user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            cart = redis_conn.hgetall(f'carts_{self.user.id}')
            sku_id_list = cart.keys()
            if selected:
                redis_conn.sadd(f'selected_{self.user.id}', *sku_id_list)
            else:
                redis_conn.delete(f'selected_{self.user.id}')
            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

        else:
            cart_str = request.COOKIES.get('carts')

            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return JsonResponse({'code':RETCODE.DBERR, 'errmsg':'cookie没有获取到'})
            for sku_id in cart_dict:
                cart_dict[sku_id]['selected'] = selected

            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response = JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
            response.set_cookie('carts', cart_str)

            return response


class CartSimpleView(View):
    """商品页面右上角购物车"""
    def get(self, request):
        if self.user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            redis_cart = redis_conn.hgetall(f'carts_{self.user.id}')
            cart_selected = redis_conn.smembers(f'selected_{self.user.id}')

            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in cart_selected
                }
        else:
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

        cart_skus = []
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'default_image_url': sku.default_image.url
            })

        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_skus': cart_skus})

