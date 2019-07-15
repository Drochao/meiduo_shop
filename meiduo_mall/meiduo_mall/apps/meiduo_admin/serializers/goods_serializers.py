from rest_framework import serializers

from goods.models import GoodsVisitCount, SPU, SpecificationOption, \
    SPUSpecification, Brand, GoodsCategory


class GoodsSerializer(serializers.ModelSerializer):
    """商品SKU序列化器"""
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GoodsVisitCount
        fields = ('count', 'category')


class SPUSimpleSerializer(serializers.ModelSerializer):
    """商品SPU表序列化器"""

    class Meta:
        model = SPU
        fields = ('id', 'name')


class SPUGoodsSerializer(serializers.ModelSerializer):
    """SPU表序列化器"""
    category1_id = serializers.IntegerField()
    category2_id = serializers.IntegerField()
    category3_id = serializers.IntegerField()
    brand_id = serializers.IntegerField()
    brand = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SPU
        exclude = ('category1', 'category2', 'category3')


class SPUOptionSerializer(serializers.ModelSerializer):
    """SPU选项序列化器"""

    class Meta:
        model = SpecificationOption
        fields = ('id', 'value')


class SPUSpecsSerializer(serializers.ModelSerializer):
    """保存商品sku序列化器"""
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()
    options = SPUOptionSerializer(many=True)

    class Meta:
        model = SPUSpecification
        exclude = ('create_time', 'update_time')


class SpecificationSerializer(serializers.ModelSerializer):
    """SPU规格序列化器"""
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()

    class Meta:
        model = SPUSpecification
        fields = ('id',
                  'name',
                  'spu',
                  'spu_id')


class SPUBrandSerializer(serializers.ModelSerializer):
    """SPU表品牌序列化器"""

    class Meta:
        model = Brand
        fields = '__all__'


class CategoriesSerializer(serializers.ModelSerializer):
    """SPU表分类信息序列化器"""

    class Meta:
        model = GoodsCategory
        fields = '__all__'
