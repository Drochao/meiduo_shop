from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers


class PermsSerializer(serializers.ModelSerializer):
    """用户权限表序列化器"""
    class Meta:
        model = Permission
        fields = '__all__'


class ContentTypeSerializer(serializers.ModelSerializer):
    """权限类型序列化器"""
    class Meta:
        model = ContentType
        fields = ('id', 'name')