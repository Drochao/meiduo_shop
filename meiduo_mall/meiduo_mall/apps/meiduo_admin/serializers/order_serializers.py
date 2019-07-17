from rest_framework import serializers

from goods.models import SKU
from orders.models import OrderInfo, OrderGoods


class SKUSerializer(serializers.ModelSerializer):
    """商品sku序列化器"""
    class Meta:
        model = SKU
        fields = ('name', 'default_image')


class OrderGoodsSerializer(serializers.ModelSerializer):
    """订单商品序列化器"""
    sku = SKUSerializer(read_only=True)

    class Meta:
        model = OrderGoods
        fields = ('count', 'price', 'sku')


class OrderSerializer(serializers.ModelSerializer):
    """商品订单序列化器"""
    user = serializers.StringRelatedField(read_only=True)
    skus = OrderGoodsSerializer(many=True, read_only=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'
