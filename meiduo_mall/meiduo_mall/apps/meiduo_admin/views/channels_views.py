from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from goods.models import GoodsChannel, GoodsChannelGroup
from meiduo_admin.serializers.channels_serializer import ChannelSerializer, ChannelGroupSimpleSerializer
from meiduo_mall.utils.pagenum import PageNum


class ChannelViewSet(ModelViewSet):
    queryset = GoodsChannel.objects.all()
    serializer_class = ChannelSerializer
    pagination_class = PageNum


class ChannelGroupView(ListAPIView):
    queryset = GoodsChannelGroup.objects.all()
    serializer_class = ChannelGroupSimpleSerializer