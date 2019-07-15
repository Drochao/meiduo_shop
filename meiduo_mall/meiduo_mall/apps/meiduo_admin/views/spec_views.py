from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SPUSpecification, SPU
from meiduo_admin.serializers.goods_serializers import SpecificationSerializer, SPUSimpleSerializer
from meiduo_mall.utils.pagenum import PageNum


class SpecViewSet(ModelViewSet):
    """规格表视图"""
    serializer_class = SpecificationSerializer
    queryset = SPUSpecification.objects.all()
    pagination_class = PageNum

    def get_queryset(self):
        if self.action == 'simple':
            return SPU.objects.all()
        return self.queryset.all()

    def get_serializer_class(self):
        if self.action == 'simple':
            return SPUSimpleSerializer
        return self.serializer_class

    @action(methods=['get'], detail=False)
    def simple(self, request):
        data = self.get_queryset()
        s = self.get_serializer(data, many=True)
        return Response(s.data)
