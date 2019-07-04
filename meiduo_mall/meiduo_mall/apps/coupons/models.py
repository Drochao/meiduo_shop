from django.db import models

from goods.models import GoodsCategory, SKU
from meiduo_mall.utils.models import BaseModel
from orders.models import OrderInfo
from users.models import User


class CouponType(models.Model):
    """优惠券种类"""

    name = models.CharField(max_length=20, unique=True, verbose_name="种类名称")

    class Meta:
        db_table = 'tb_coupon_type'
        verbose_name = '优惠券种类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CouponInfo(BaseModel):
    """优惠券仓库"""

    name = models.CharField(max_length=20, null=True, blank=True, verbose_name="优惠券标题")
    # img = models.ImageField(verbose_name='图片')
    count = models.IntegerField(default=0, verbose_name='剩余库存')
    status = models.BooleanField(default=True, verbose_name="全部券是否有效")
    receive = models.BooleanField(default=True, verbose_name="是否可以领取")
    limit = models.IntegerField(default=0, verbose_name='每人限领')
    start_date = models.DateField(auto_now_add=True, verbose_name='允许领取日')  # auto_now_add 为添加时的日期
    end_date = models.DateField(verbose_name='结束领取日')
    after_day = models.IntegerField(default=0, verbose_name='领取多少天内有效')  # 0为结束领取日,
    type = models.ForeignKey(CouponType, on_delete=models.CASCADE, verbose_name='优惠券种类')
    select_str = models.CharField(max_length=50, default="", verbose_name="可用范围描述")
    security_level = models.IntegerField(default=0, verbose_name='保密等级')  # 0-公开随便可领取
    skus = models.ManyToManyField(SKU)  # 与SKU表进行多对多关联
    category = models.ManyToManyField(GoodsCategory)  # 与分类表进行多对多关联

    class Meta:
        db_table = 'tb_coupon_info'
        verbose_name = '优惠券种类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CouponDetail(BaseModel):
    """优惠券持有表"""

    # 领取日期=create_time
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    coupon = models.ForeignKey(CouponInfo, related_name='details', on_delete=models.CASCADE, verbose_name='优惠券')
    status = models.BooleanField(default=True, verbose_name="是否有效")
    # is_used = models.BooleanField(default=False, verbose_name="是否已用")
    order = models.ForeignKey(OrderInfo, null=True, blank=True, on_delete=models.CASCADE, verbose_name='用于订单')

    class Meta:
        db_table = 'tb_coupon_detail'
        verbose_name = '优惠券持有表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s' % (self.user, self.coupon)


class CouponRule(BaseModel):
    """优惠券规则"""

    name = models.CharField(max_length=20, verbose_name="规则的名称")
    key = models.CharField(max_length=20, verbose_name="规则键名")
    type = models.ForeignKey(CouponType, related_name='rules', on_delete=models.CASCADE, verbose_name='所属种类')

    class Meta:
        db_table = 'tb_coupon_rule'
        verbose_name = '优惠券规则'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CouponOption(BaseModel):
    """规则选项"""

    rule = models.ForeignKey(CouponRule, on_delete=models.CASCADE, verbose_name='所属规则')
    value = models.CharField(max_length=20, verbose_name="选项")

    class Meta:
        db_table = 'tb_coupon_option'
        verbose_name = '规则选项'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.value


class CouponComb(BaseModel):
    """优惠券规则-选项组合"""

    coupon = models.ForeignKey(CouponInfo, related_name='combs', on_delete=models.CASCADE, verbose_name='所属优惠券')
    rule = models.ForeignKey(CouponRule, on_delete=models.CASCADE, verbose_name='所属规则')
    option = models.ForeignKey(CouponOption, on_delete=models.CASCADE, verbose_name='所属选项')

    class Meta:
        db_table = 'tb_coupon_comb'
        verbose_name = '规则选项组合'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s - %s' % (self.coupon, self.rule.name, self.option.value)

# class SelectCategory(models.Model):
#     """指定分类范围 - 中间表"""
#
#     category = models.ForeignKey(GoodsCategory, on_delete=models.CASCADE, verbose_name='指定分类')
#     coupon = models.ForeignKey(CouponInfo, on_delete=models.CASCADE, verbose_name='所属优惠券')
#
#     class Meta:
#         db_table = 'tb_select_category'
#         verbose_name = '指定分类范围'
#         verbose_name_plural = verbose_name

# class SelectSku(models.Model):
#     """指定sku范围 - 中间表"""
#
#     sku = models.ForeignKey(SKU, on_delete=models.CASCADE, verbose_name='指定sku')
#     coupon = models.ForeignKey(CouponInfo, on_delete=models.CASCADE, verbose_name='所属优惠券')
#
#     class Meta:
#         db_table = 'tb_select_sku'
#         verbose_name = '指定sku范围'
#         verbose_name_plural = verbose_name
