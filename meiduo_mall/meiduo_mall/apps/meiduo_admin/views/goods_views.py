from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SPU, SPUSpecification
from meiduo_admin.serializers.goods_serializers import SPUSimpleSerializer, SPUSpecsSerializer, SPUGoodsSerializer
from meiduo_mall.utils.pagenum import PageNum


class GoodsViewSet(ModelViewSet):
    pagination_class = PageNum
    serializer_class = SPUGoodsSerializer
    queryset = SPU.objects.all()

    def get_queryset(self):
        if self.action == 'simple':
            return SPU.objects.all()
        if self.action == 'specs':
            pk = self.kwargs['pk']
            if pk:
                return SPUSpecification.objects.filter(spu_id=pk)
            return SPUSpecification.objects.all()
        return self.queryset.all()

    def get_serializer_class(self):
        if self.action == 'simple':
            return SPUSimpleSerializer

        if self.action == 'specs':
            return SPUSpecsSerializer
        return self.serializer_class

    @action(methods=['get'], detail=False)
    def simple(self, request):
        data = self.get_queryset()
        s = self.get_serializer(data, many=True)

        return Response(s.data)

    @action(methods=['get'], detail=False)
    def specs(self, request, pk):
        data = self.get_queryset()
        s = self.get_serializer(data, many=True)
        return Response(s.data)


