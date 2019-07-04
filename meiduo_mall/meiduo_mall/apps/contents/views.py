import json

from django import http
from django.shortcuts import render

from django.views import View

from contents.models import ContentCategory
from contents.utils import get_categories
from meiduo_mall.utils.response_code import RETCODE


class IndexView(View):
    """主页"""

    def get(self, request):
        """渲染主页"""

        categories = get_categories()

        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        context = {
            'categories': categories,
            'contents': contents
        }

        return render(request, 'index.html', context)


class GetWeatherView(View):
    """获取天气"""
    def post(self, request):
        json_dict = json.loads(request.body)
        all_weather_date = json_dict.get('all_weather_date')
        today = all_weather_date["data"][0]["day"]
        today1 = today[:2]
        weather_name = ["lei", "qing", "shachen", "taifeng", "wu", "xue", "yin", "yu",
                        "yun", "zhenyu"]
        if all_weather_date["data"][0]["wea_img"] not in weather_name:
            str_path = "55"
        else:
            str_path = str(all_weather_date["data"][0]["wea_img"])
        if all_weather_date != "qing" or "wu" or "xue":
            title_about = '  今日推荐:  买手机，宅在家里玩'
        else:
            title_about = "  今日推荐:  买电脑，适合和小伙伴开黑"

        return http.JsonResponse({'code': RETCODE.OK, "errmsg": "OK", 'weather': [str_path, title_about, today1]})


