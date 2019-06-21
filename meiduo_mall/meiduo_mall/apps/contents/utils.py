from goods.models import GoodsChannel


def get_categories():
    """返回商品类别数据"""
    categories = {}

    goods_channels_qs = GoodsChannel.objects.order_by('group_id', 'sequence')
    for channel in goods_channels_qs:
        group_id = channel.group_id

        if group_id not in categories:
            categories[group_id] = {
                'channels': [],
                'sub_cats': []}

        cat1 = channel.category
        cat1.url = channel.url

        categories[group_id]['channels'].append(cat1)

        cat2_qs = cat1.subs.all()
        for cat2 in cat2_qs:
            cat3_qs = cat2.subs.all()
            cat2.sub_cats = cat3_qs
            categories[group_id]['sub_cats'].append(cat2)

    return categories
