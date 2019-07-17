from django.conf import settings
from fdfs_client.client import Fdfs_client
from rest_framework import serializers

from goods.models import Brand


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = (
            'id',
            'name',
            'logo',
            'first_letter'
        )

    def create(self, validated_data):
        file = validated_data.pop('logo')
        content = file.read()

        conn = Fdfs_client(settings.FDFS_CONFPATH)

        res = conn.upload_by_buffer(content)
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError('上传失败')

        validated_data['logo'] = res['Remote file_id'].replace('\\', '/')
        return super().create(validated_data)

    def update(self, instance, validated_data):
        file = validated_data.pop('logo')
        content = file.read()

        conn = Fdfs_client(settings.FDFS_CONFPATH)

        res = conn.upload_by_buffer(content)
        if res['Status'] != 'Upload successed.':
            raise serializers.ValidationError('上传失败!')

        logo = res['Remote file_id'].replace('\\', '/')
        instance.logo = logo
        super().update(validated_data)
        return super().update(validated_data)