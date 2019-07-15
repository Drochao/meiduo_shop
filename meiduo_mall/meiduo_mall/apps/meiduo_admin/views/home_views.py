from datetime import timedelta

import pytz
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from goods.models import GoodsVisitCount
from meiduo_admin.serializers.goods_serializers import GoodsSerializer
from users.models import User


class HomeViewSet(ViewSet):
    # 指定管理员权限
    # 虽然token一般只有超管才有，但是存在超管降级或者超管权限变更的情况，所以还需要
    # 判断身份
    permission_classes = [IsAdminUser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.date_0_shanghai = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE)). \
            replace(hour=0, minute=0, second=0)
        # print(self.date_0_shanghai)
        # self.now_date = timezone.now().date()
        # print(self.now_date)

    def response(self, count):
        return {
            'count': count,
            'date': self.date_0_shanghai.date()
        }

    @action(methods=['get'], detail=False)
    def total_count(self, request):
        """用户总数"""
        count = User.objects.count()
        return Response(self.response(count))

    @action(methods=['get'], detail=False)
    def day_increment(self, request):
        """日增用户数"""
        count = User.objects.filter(date_joined__gte=self.date_0_shanghai).count()
        return Response(self.response(count))

    @action(methods=['get'], detail=False)
    def day_active(self, request):
        """今日活跃人数"""
        count = User.objects.filter(last_login__gte=self.date_0_shanghai).count()
        return Response(self.response(count))

    @action(methods=['get'], detail=False)
    def day_orders(self, request):
        """今日下单用户数"""
        user_queryset = User.objects.filter(orderinfo__create_time__gte=self.date_0_shanghai)
        count = len(set(user_queryset))
        return Response(self.response(count))

    @action(methods=['get'], detail=False)
    def month_increment(self, request):
        """月增用户数量"""
        cur_date = timezone.now().astimezone(pytz.timezone(settings.TIME_ZONE))

        start_day = cur_date - timedelta(29)

        date_list = []

        for i in range(30):
            index_date = (start_day + timedelta(i)).replace(hour=0, minute=0, second=0)

            cur_date = index_date + timedelta(1)

            count = User.objects.filter(date_joined__gte=index_date, date_joined__lt=cur_date).count()

            date_list.append({
                'count': count,
                'date': index_date.date()
            })

        return Response(date_list)

    @action(methods=['get'], detail=False)
    def goods_day_views(self, request):
        """商品访问数量"""
        data = GoodsVisitCount.objects.filter(create_time__gte=self.date_0_shanghai)

        ser = GoodsSerializer(data, many=True)

        return Response(ser.data)
