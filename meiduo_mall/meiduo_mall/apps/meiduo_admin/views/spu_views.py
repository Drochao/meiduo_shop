from rest_framework.generics import ListAPIView

from goods.models import Brand, GoodsCategory
from meiduo_admin.serializers.goods_serializers import SPUBrandSerializer, CategoriesSerializer


class SPUBrandView(ListAPIView):
    """获取SPU表的品牌信息"""
    serializer_class = SPUBrandSerializer
    queryset = Brand.objects.all()


class ChannelCategoryView(ListAPIView):
    """获取spu一级分类"""
    serializer_class = CategoriesSerializer
    queryset = GoodsCategory.objects.filter(parent=None)

    def get_queryset(self):
        try:
            pk = self.kwargs['pk']
            if pk:
                return GoodsCategory.objects.filter(parent=pk)
        except Exception as e:
            print(e)
        return self.queryset.all()

