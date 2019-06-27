from django import http
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from contents.utils import get_categories
from goods import constants
from goods.models import SKU, GoodsCategory, GoodsVisitCount
from goods.utils import get_breadcrumb
from meiduo_mall.utils.response_code import RETCODE


class ListView(View):
    """商品列表页"""
    def get(self, request, category_id, page_num):
        """提供商品列表页"""
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseNotFound('GoodsCategory does not exist')

        sort = request.GET.get('sort', 'default')

        categories = get_categories()

        breadcrumb = get_breadcrumb(category)

        if sort == 'price':
            sort_field = 'price'
        elif sort == 'hot':
            sort_field = '-sales'
        else:
            sort = 'default'
            sort_field = 'create_time'

        skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by(sort_field)

        paginator = Paginator(skus, constants.GOODS_LIST_LIMIT)

        try:
            page_skus = paginator.page(page_num)
        except EmptyPage:
            return http.HttpResponseNotFound('empty page')

        total_page = paginator.num_pages

        context = {
            'categories': categories,   # 频道分类
            'breadcrumb': breadcrumb,   # 面包屑导航
            'sort': sort,               # 排序字段
            'category': category,       # 第三级分类
            'page_skus': page_skus,     # 分页后数据
            'total_page': total_page,   # 总页数
            'page_num': page_num,       # 当前页码
        }
        return render(request, 'list.html', context)


class HotGoodsView(View):
    """商品热销排行"""
    def get(self, request, category_id):
        """提供商品热销排行JSON数据"""
        #
        skus = SKU.objects.filter(category_id=category_id, is_launched=True)

        hot_skus = []
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            })
        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'OK', 'hot_skus':hot_skus})


class DetailView(View):
    """商品详情页"""

    def get(self, request, sku_id):
        """提供商品详情页"""
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')

        categories = get_categories()
        category = sku.category
        breadcrumb = get_breadcrumb(category)

        spu = sku.spu

        current_sku_spec_qs = sku.specs.order_by('spec_id')
        current_sku_option_ids = []
        for current_sku_spec in current_sku_spec_qs:
            current_sku_option_ids.append(current_sku_spec.option_id)

        temp_sku_qs = spu.sku_set.all()
        spec_sku_map = {}

        for temp_sku in temp_sku_qs:
            temp_spec_qs = temp_sku.specs.order_by('spec_id')
            temp_sku_option_ids = []
            for temp_spec in temp_spec_qs:
                temp_sku_option_ids.append(temp_spec.option_id)
            spec_sku_map[tuple(temp_sku_option_ids)] = temp_sku.id

        spu_spec_qs = spu.specs.order_by('id')

        for index, spec in enumerate(spu_spec_qs):
            spec_option_qs = spec.options.all()
            temp_option_ids = current_sku_option_ids[:]
            for option in spec_option_qs:
                temp_option_ids[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(temp_option_ids))

            spec.spec_options = spec_option_qs

        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'category': category,
            'spu': spu,
            'spec_qs': spu_spec_qs
        }
        return render(request, 'detail.html', context)


class DetailVisitView(View):
    """详情页分类商品访问量"""
    def post(self, request, category_id):
        try:
            GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('缺少必传参数')

        today_date = timezone.now()

        try:
            counts_data = GoodsVisitCount.objects.get(date=today_date, category_id=category_id)
        except GoodsVisitCount.DoesNotExist:
            counts_data = GoodsVisitCount(category_id=category_id)
        counts_data.count += 1
        counts_data.save()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})