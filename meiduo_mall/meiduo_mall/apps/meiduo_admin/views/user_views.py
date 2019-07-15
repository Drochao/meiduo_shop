from rest_framework.generics import ListCreateAPIView

from meiduo_admin.serializers.user_serializers import UserSerializer
from meiduo_mall.utils.pagenum import PageNum
from users.models import User


class UserView(ListCreateAPIView):
    serializer_class = UserSerializer
    pagination_class = PageNum
    queryset = User.objects.all()

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')

        if keyword:
            return User.objects.filter(username__startswith=keyword)

        return self.queryset.all()
