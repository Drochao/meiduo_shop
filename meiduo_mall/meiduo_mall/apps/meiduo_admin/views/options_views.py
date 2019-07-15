from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SpecificationOption, SPUSpecification
from meiduo_admin.serializers.option_serializers import OptionSerializer
from meiduo_mall.utils.pagenum import PageNum


class OptionsViewSet(ModelViewSet):
    """规格选项表的增删改查"""
    serializer_class = OptionSerializer
    queryset = SpecificationOption.objects.all()
    pagination_class = PageNum

    # def get_queryset(self):
    #     if self.action == 'simple':
    #         return SpecificationOption.objects.all()
    #
    # def get_serializer_class(self):
    #     if self.action == 'simple':
    #         return SpecificationSerializer
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        dat = serializer.data
        spec_id = dat['spec_id']
        spu_id = SPUSpecification.objects.get(id=spec_id).spu_id
        dat['spu_id'] = spu_id
        return Response(dat)

    # def list(self, request, *args, **kwargs):
    #     data = self.get_queryset()
    #     page = self.paginate_queryset(data)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         for i in serializer.data:
    #             spec_id = i['spec_id']
    #             i['spu_id'] = SPUSpecification.objects.get(id=spec_id).spu_id
    #         return self.get_paginated_response(serializer.data)
    #
    #     serializer = self.get_serializer(data, many=True)
    #
    #     # response =
    #     return Response(serializer.data)

