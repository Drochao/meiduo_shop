from rest_framework import serializers

from goods.models import SKU


class SKUSerializer(serializers.ModelSerializer):
    """商品SKU序列化器"""
    # name = serializers.CharField(label='名称', max_length=50)
    # caption = serializers.CharField(label='副标题', max_length=100, required=False)
    # spu = serializers.PrimaryKeyRelatedField(label='商品', read_only=True)
    # category = serializers.PrimaryKeyRelatedField(label='从属类别', read_only=True)
    # price = serializers.DecimalField(label='单价', max_digits=10, decimal_places=2)
    # cost_price = serializers.DecimalField(label='进价', required=False, max_digits=10, decimal_places=2)
    # market_price = serializers.DecimalField(label='市场价', required=False, max_digits=10, decimal_places=2)
    # stock = serializers.IntegerField(label='库存', required=False)
    # sales = serializers.IntegerField(label='销量', required=False)
    # comments = serializers.IntegerField(label='评价数', required=False)
    # is_launched = serializers.BooleanField(label='是否上架销售', required=False)
    # default_image = serializers.ImageField(label='默认图片', max_length=200, required=False)
    class Meta:
        model = SKU
        fields = '__all__'

    def create(self, validated_data):
        """新建"""
        return SKU.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """更新，instance为要更新的对象实例"""
        instance.name = validated_data.get('name', instance.name)
        instance.caption = validated_data.get('caption', instance.caption)
        instance.price = validated_data.get('price', instance.price)
        instance.cost_price = validated_data.get('cost_price', instance.cost_price)
        instance.market_price = validated_data.get('market_price', instance.market_price)
        instance.stock = validated_data.get('sales', instance.sales)
        instance.sales = validated_data.get('stock', instance.stock)
        instance.comments = validated_data.get('comments', instance.comments)
        instance.is_launched = validated_data.get('is_launched', instance.is_launched)
        instance.default_image = validated_data.get('default_image', instance.default_image)
        instance.save()
        return instance
