import logging

from django.core.cache import cache
from django.http import JsonResponse
from django.views import View

from .models import Area
from meiduo_mall.utils.response_code import RETCODE

logger = logging.getLogger('django')


class AreasView(View):
    """省市区数据查询"""
    def get(self, request):
        """提供省市区数据"""
        area_id = request.GET.get('area_id')
        # 如果area_id为空，返回省数据
        if not area_id:
            # 从缓存获取省数据
            province_list = cache.get('province_list')
            # 如果没有，从mysql取
            if not province_list:
                try:
                    province_model_list = Area.objects.filter(parent__isnull=True)

                    province_list = []

                    for province_model in province_model_list:
                        province_list.append({'id': province_model.id, 'name': province_model.name})
                except Exception as e:
                    logger.error(e)
                    return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '省份数据错误'})
                # 把数据缓存起来
                cache.set('province_list', province_list, 3600)

            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
        else:
            # 从缓存获取市/区数据
            sub_data = cache.get('sub_area_' + area_id)

            if not sub_data:
                try:
                    parent_model = Area.objects.get(id=area_id)
                    sub_model_list = parent_model.subs.all()

                    sub_list = []
                    for sub_model in sub_model_list:
                        sub_list.append({'id': sub_model.id, 'name': sub_model.name})

                    sub_data = {
                        'id': parent_model.id,
                        'name': parent_model.name,
                        'subs': sub_list
                    }
                except Exception as e:
                    logger.error(e)
                    return JsonResponse({'code': RETCODE.DBERR, 'errmsg': '城市或区域数据错误'})

                cache.set('sub_area_' + area_id, sub_data, 3600)

            return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
