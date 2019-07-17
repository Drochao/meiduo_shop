from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.admin_serializers import AdminSerializer
from meiduo_mall.utils.pagenum import PageNum
from users.models import User


class AdminView(ModelViewSet):
    serializer_class = AdminSerializer

    queryset = User.objects.filter(is_staff=True)

    pagination_class = PageNum
