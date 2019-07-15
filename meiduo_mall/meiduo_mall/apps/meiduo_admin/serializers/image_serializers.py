from rest_framework import serializers

from goods.models import SKUImage, SKU


class ImageSerializer(serializers.ModelSerializer):
    sku = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SKUImage
        fields = ('sku', 'image', 'id')


class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ('id', 'name')