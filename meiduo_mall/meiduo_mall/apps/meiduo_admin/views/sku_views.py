from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SKU, GoodsCategory, SKUSpecification
from meiduo_admin.serializers.image_serializers import SKUSerializer
from meiduo_admin.serializers.skus_serializers import SKUGoodsSerializer, CategoriesSerializer
from meiduo_mall.utils.pagenum import PageNum


class SKUGoodsViewSet(ModelViewSet):
    queryset = SKU.objects.all()
    serializer_class = SKUGoodsSerializer

    pagination_class = PageNum

    def get_queryset(self):
        if self.action == 'categories':
            return GoodsCategory.objects.filter(parent_id__gt=37)

        keyword = self.request.query_params.get('keyword')

        if keyword:
            return self.queryset.filter(name__icontains=keyword)
        return self.queryset.all()

    def get_serializer_class(self):
        if self.action == 'categories':
            return CategoriesSerializer
        if self.action == 'simple':
            return SKUSerializer

        return self.serializer_class

    # def create(self, request, *args, **kwargs):
    #     data = request.data
    #     serializer = self.get_serializer(data=data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #
    #     specs = data['specs']
    #
    #     for s in specs:
    #         s['sku_id'] = serializer.data['id']
    #         SKUSpecification.objects.create(**s)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['get'], detail=False)
    def categories(self, request):
        """获取商品分类信息"""
        cates = self.get_queryset()
        s = self.get_serializer(cates, many=True)
        return Response(s.data)

    @action(methods=['get'], detail=False)
    def simple(self, request):
        data = self.get_queryset()
        s = self.get_serializer(data, many=True)
        return Response(s.data)