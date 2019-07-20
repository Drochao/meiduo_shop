# !/home/drochao/Desktop/meiduo/meiduo_shop/meiduo_mall/venv python3
import sys

from django.conf import settings
from django.template import loader

from contents.utils import get_categories
from goods import models
from goods.models import SKU
from goods.utils import get_breadcrumb

sys.path.insert(0, '../')

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meiduo_mall.settings.dev')

import django
django.setup()

def generate_static_sku_detail_html(sku_id):
    """generate static goods detail html"""
    sku = SKU.objects.get(id=sku_id)

    category = sku.category
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
        'categories': get_categories(),
        'breadcrumb': get_breadcrumb(category),
        'sku': sku,
        'category': category,
        'spu': spu,
        'spec_qs': spu_spec_qs,
    }

    template = loader.get_template('detail.html')
    html_text = template.render(context)
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'details/' + str(sku_id) + '.html')
    with open(file_path, 'w') as f:
        f.write(html_text)


if __name__ == '__main__':
    skus = models.SKU.objects.all()
    for sku in skus:
        print(sku.id)
        generate_static_sku_detail_html(sku.id)