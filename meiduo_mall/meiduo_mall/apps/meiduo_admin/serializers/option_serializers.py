from rest_framework import serializers

from goods.models import SpecificationOption
from meiduo_admin.serializers.goods_serializers import SPUSpecsSerializer


class OptionSerializer(serializers.ModelSerializer):
    # specs = SPUSpecsSerializer()
    spec = serializers.StringRelatedField()
    spec_id = serializers.IntegerField()

    class Meta:
        model = SpecificationOption

        # fields = ('spec', 'id', 'value')
        fields = ('spec', 'id', 'value', 'spec_id')
