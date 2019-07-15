from rest_framework import serializers

from goods.models import GoodsCategory, SKUSpecification, SKU


class CategoriesSerializer(serializers.ModelSerializer):
    """商品分类序列化器"""

    class Meta:
        model = GoodsCategory
        fields = ('id', 'name')


class SKUSpecificationSerializer(serializers.ModelSerializer):
    """SKU规格表序列化器"""
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification
        fields = ('spec_id', 'option_id')


class SKUGoodsSerializer(serializers.ModelSerializer):
    """获取sku信息的序列化器"""
    specs = SKUSpecificationSerializer(many=True)

    category_id = serializers.IntegerField()

    category = serializers.StringRelatedField(read_only=True)

    spu_id = serializers.IntegerField()

    spu = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SKU
        fields = '__all__'

    def create(self, validated_data):
        specs = validated_data.pop('specs')

        instance = super().create(validated_data)

        for item in specs:
            item['sku_id'] = instance.id
            SKUSpecification.objects.create(**item)

        return instance

    def update(self, instance, validated_data):
        specs = validated_data.pop('specs')

        SKUSpecification.objects.filter(sku_id=instance.id).delete()

        for item in specs:
            item['sku_id'] = instance.id
            SKUSpecification.objects.create(**item)

        return super().update(instance, validated_data)
