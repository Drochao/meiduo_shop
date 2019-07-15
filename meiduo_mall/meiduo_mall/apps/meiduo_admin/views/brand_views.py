from rest_framework.viewsets import ModelViewSet

from goods.models import Brand
from meiduo_admin.serializers.brand_serializers import BrandSerializer
from meiduo_mall.utils.pagenum import PageNum


class BrandViewSet(ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    pagination_class = PageNum