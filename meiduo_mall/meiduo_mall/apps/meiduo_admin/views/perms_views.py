from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.perms_serializers import PermsSerializer, ContentTypeSerializer
from meiduo_mall.utils.pagenum import PageNum


class PermsViewSet(ModelViewSet):
    serializer_class = PermsSerializer
    queryset = Permission.objects.all()
    pagination_class = PageNum


class ContentTypes(ListAPIView):
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializer
