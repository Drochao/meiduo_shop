import json
import logging
from decimal import Decimal

from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.http import HttpResponseForbidden, JsonResponse, HttpResponseNotFound
from django.shortcuts import render
from django.utils import timezone
from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredView
from orders import constants
from orders.models import OrderInfo, OrderGoods
from users.models import Address


logger = logging.getLogger('django')


class OrderSettlementView(LoginRequiredView):
    """结算订单"""

    def get(self, request):
        """提供订单结算页面"""
        user = request.user
        # 查询当前登陆用户的所有收货地址
        addresses = Address.objects.filter(user=request.user, is_deleted=False)
        # 判断用户是否有收获地址
        if not addresses:
            addresses = None
        # 创建redis连接对象
        redis_conn = get_redis_connection('carts')
        # 获取redis购物车的hash数据
        redis_cart = redis_conn.hgetall(f'carts_{user.id}')
        # 获取勾选状态，set集合数据
        cart_selected = redis_conn.smembers(f'selected_{user.id}')
        # 只要勾选商品数据
        cart = {}  # {sku_id:count, sku_id:count}

        for sku_id in cart_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])

        total_count = 0
        total_amount = Decimal(0.00)

        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]
            sku.amount = sku.count * sku.price

            total_count += sku.count
            total_amount += sku.count * sku.price

        freight = Decimal('10.00')

        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight
        }
        return render(request, 'place_order.html', context)


class OrderCommitView(LoginRequiredView):
    """订单提交"""

    def post(self, request):
        """保存订单信息和订单商品信息"""

        # 获取数据
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')

        if not all([address_id, pay_method]):
            return HttpResponseForbidden("缺少必传参数")
        try:
            address = Address.objects.get(id=address_id)
        except Exception:
            return HttpResponseForbidden("参数address_id有误")
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPY']]:
            return HttpResponseForbidden('参数pay_method有误')

        # 获取登录用户
        user = request.user

        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)

        with transaction.atomic():
            save_id = transaction.savepoint()

            try:
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_amount=Decimal('0'),
                    total_count=0,
                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPY']
                    else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )

                redis_conn = get_redis_connection('carts')
                redis_cart = redis_conn.hgetall(f'carts_{user.id}')
                selected = redis_conn.smembers(f'selected_{user.id}')
                carts = {}
                for sku_id in selected:
                    carts[int(sku_id)] = int(redis_cart[sku_id])
                sku_ids = carts.keys()

                for sku_id in sku_ids:
                    while True:
                        sku = SKU.objects.get(id=sku_id)
                        buy_count = carts[sku_id]

                        origin_stock = sku.stock
                        origin_sales = sku.sales

                        if buy_count > origin_stock:
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})

                        new_stock = origin_stock - buy_count
                        new_sales = origin_sales + buy_count

                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)

                        if result == 0:
                            continue

                        sku.spu.sales += buy_count
                        sku.spu.save()

                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=buy_count,
                            price=sku.price
                        )

                        order.total_count += buy_count
                        order.total_amount += (buy_count * sku.price)
                        # 等商品下单成功后结束循环
                        break

                order.total_amount += order.freight
                order.save()
            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})

            transaction.savepoint_commit(save_id)

        with redis_conn.pipeline() as pl:
            pl.hdel(f'carts_{user.id}', *selected)
            pl.srem(f'selected_{user.id}', *selected)
            pl.execute()

        return JsonResponse({'code': RETCODE.OK, 'errmsg': '下单成功', 'order_id': order.order_id})


class OrderSuccessView(LoginRequiredView):
    """提交订单成功"""

    def get(self, request):
        json_dict = request.GET
        order_id = json_dict.get('order_id')
        payment_amount = json_dict.get('payment_amount')
        payment_method = json_dict.get('pay_method')

        try:
            OrderInfo.objects.get(order_id=order_id, pay_method=payment_method, total_amount=payment_amount)
        except OrderInfo.DoesNotExist:
            return HttpResponseForbidden('订单有误')

        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': payment_method
        }
        return render(request, 'order_success.html', context)


class OrderInfoView(LoginRequiredView):
    """订单信息"""

    def get(self, request, page_num):
        """渲染订单信息页面"""
        # 获取按时间顺序的订单信息查询集
        orders = OrderInfo.objects.filter(user_id=request.user.id).order_by('-create_time')
        # 分页
        paginator = Paginator(orders, constants.ORDER_LIST_LIMIT)
        try:
            # 获取分页后数据
            page_orders = paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('empty page')
        # 获取总页数
        total_page = paginator.num_pages
        # 给page_order新增sku_list属性
        for order in page_orders:
            order.sku_list = []
            goods = order.skus.all()
            # 本来sku_list数据是sku表的,给他新增两个属性，count和amount
            for good in goods:
                sku = SKU.objects.get(id=good.sku_id)
                sku.count = OrderGoods.objects.get(order_id=order.order_id, sku_id=good.sku_id).count
                sku.amount = sku.price * sku.count
                order.sku_list.append(sku)

        context = {
            'page_orders': page_orders,  # 分页后数据
            'page_num': page_num,  # 当前分页
            'total_page': total_page,  # 总页数
        }

        return render(request, 'user_center_order.html', context)


class CommentView(LoginRequiredView):

    def get(self, request):
        order_id = request.GET.get('order_id')
        uncomment_goods = OrderGoods.objects.filter(is_commented=False, order_id=order_id)
        uncomment_goods_list = []
        for uncomment_good in uncomment_goods:
            sku = SKU.objects.get(id=uncomment_good.sku_id)
            uncomment_goods_list.append({
                'sku_id': uncomment_good.sku_id,
                'score': uncomment_good.score,
                'order_id': order_id,
                'comment': uncomment_good.comment,
                'is_anonymous': "false",
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': str(sku.price),
            })
        context = {
            'uncomment_goods_list': uncomment_goods_list
        }
        return render(request, 'goods_judge.html', context)

    def post(self, request):
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        comment = json_dict.get('comment')
        order_id = json_dict.get('order_id')
        selected = json_dict.get('is_anonymous')
        score = json_dict.get('score')

        if not all([sku_id, comment, order_id, score]):
            return HttpResponseForbidden('缺少必传参数')

        good = OrderGoods.objects.get(order_id=order_id, sku_id=sku_id)
        good.is_commented = True
        good.comment = comment
        good.is_anonymous = selected
        good.score = score
        good.save()
        OrderInfo.objects.filter(
            order_id=order_id,
            status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT']).update(status=OrderInfo.ORDER_STATUS_ENUM['FINISHED'])
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})
