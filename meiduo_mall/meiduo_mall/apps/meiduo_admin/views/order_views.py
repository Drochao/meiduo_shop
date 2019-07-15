from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.order_serializers import OrderSerializer
from meiduo_mall.utils.pagenum import PageNum
from orders.models import OrderInfo


class OrderViewSet(ModelViewSet):
    pagination_class = PageNum
    queryset = OrderInfo.objects.all()
    serializer_class = OrderSerializer