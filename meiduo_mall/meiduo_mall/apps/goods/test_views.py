from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SKU
from goods.serializers import SKUSerializer


class SKUDetailView(GenericAPIView):
    queryset = SKU.objects.all()
    serializer_class = SKUSerializer

    def get(self, request, pk):
        sku = self.get_object()
        serializer = self.get_serializer(sku)
        return Response(serializer.data)


