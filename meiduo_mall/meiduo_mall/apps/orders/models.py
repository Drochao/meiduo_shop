from django.db import models

from goods.models import SKU
from meiduo_mall.utils.models import BaseModel
from users.models import User, Address


class OrderInfo(BaseModel):
    """订单信息"""
    PAY_METHODS_ENUM = {
        'CASH': 1,
        'ALIPY': 2
    }

    PAY_METHOD_CHOICES = {
        (1, '货到付款'),
        (2, '支付宝')
    }

    ORDER_STATUS_ENUM = {
        "UNPAID": 1,
        "UNSEND": 2,
        "UNRECEIVED": 3,
        "UNCOMMENT": 4,
        "FINISHED": 5
    }

    ORDER_STATUS_CHOICES = (
        (1, "待支付"),
        (2, "待发货"),
        (3, "待收货"),
        (4, "待评价"),
        (5, "已完成"),
        (6, "已取消"),
    )

    order_id = models.CharField("订单号", max_length=64, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="下单用户")
    address = models.ForeignKey(Address, on_delete=models.PROTECT, verbose_name="收货地址")
    total_count = models.IntegerField("商品总数", default=1)
    total_amount = models.DecimalField("商品总金额", max_digits=10, decimal_places=2)
    freight = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="运费")
    pay_method = models.SmallIntegerField("支付方式", choices=PAY_METHOD_CHOICES, default=1)
    status = models.SmallIntegerField("订单状态", choices=ORDER_STATUS_CHOICES, default=1)

    class Meta:
        db_table = "tb_order_info"
        verbose_name = '订单基本信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.order_id


class OrderGoods(BaseModel):
    """订单商品"""
    SCORE_CHOICES = (
        (0, '0分'),
        (1, '20分'),
        (2, '40分'),
        (3, '60分'),
        (4, '80分'),
        (5, '100分'),
    )
    order = models.ForeignKey(OrderInfo, related_name='skus', on_delete=models.CASCADE, verbose_name="订单")
    sku = models.ForeignKey(SKU, on_delete=models.PROTECT, verbose_name="订单商品")
    count = models.IntegerField("数量", default=1)
    price = models.DecimalField("单价", max_digits=10, decimal_places=2)
    comment = models.TextField("评价信息", default="")
    score = models.SmallIntegerField('满意度评分', choices=SCORE_CHOICES, default=5)
    is_anonymous = models.BooleanField('是否匿名评价', default=False)
    is_commented = models.BooleanField('是否评价了', default=False)

    class Meta:
        db_table = "tb_order_goods"
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sku.name