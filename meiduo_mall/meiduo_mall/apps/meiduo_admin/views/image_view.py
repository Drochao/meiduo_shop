from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SKUImage, SKU
from meiduo_admin.serializers.image_serializers import ImageSerializer, SKUSerializer
from meiduo_mall.utils.pagenum import PageNum


class ImageViewSet(ModelViewSet):
    serializer_class = ImageSerializer

    queryset = SKUImage.objects.all()

    pagination_class = PageNum

