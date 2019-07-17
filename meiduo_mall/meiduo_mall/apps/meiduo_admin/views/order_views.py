from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.order_serializers import OrderSerializer
from meiduo_mall.utils.pagenum import PageNum
from orders.models import OrderInfo


class OrderViewSet(ModelViewSet):
    pagination_class = PageNum
    queryset = OrderInfo.objects.all()
    serializer_class = OrderSerializer

    @action(methods=['patch'], detail=True)
    def status(self, request, pk):
        order = self.get_object()
        status = request.data.get('status')
        order.status = status
        order.save()
        ser = self.get_serializer(order)
        return Response({
            'order_id': order.order_id,
            'status': status
        })
