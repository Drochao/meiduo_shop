from django.contrib.auth.models import Group, Permission
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from meiduo_admin.serializers.groups_serializers import GroupsSerializer
from meiduo_admin.serializers.perms_serializers import PermsSerializer
from meiduo_mall.utils.pagenum import PageNum


class GroupsViewSet(ModelViewSet):
    serializer_class = GroupsSerializer
    queryset = Group.objects.all()
    pagination_class = PageNum

    @action(methods=['get'], detail=False)
    def simple(self, request):
        data = self.get_queryset()
        s = self.get_serializer(data, many=True)
        return Response(s.data)


class GroupSimpleView(ListAPIView):
    serializer_class = PermsSerializer
    queryset = Permission.objects.all()
