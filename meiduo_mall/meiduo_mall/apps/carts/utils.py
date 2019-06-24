import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response):
    cart_str = request.COOKIES.get('carts')

    if cart_str is None:
        return

    cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))

    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()

    user = request.user

    for sku_id in cart_dict:
        pl.hset(f'carts_{user.id}', sku_id, cart_dict[sku_id]['count'])
        if cart_dict[sku_id]['selected']:
            pl.sadd(f'selected_{user.id}', sku_id)
        else:
            pl.srem(f'selected_{user.id}', sku_id)

    pl.execute()
    response.delete_cookie('carts')