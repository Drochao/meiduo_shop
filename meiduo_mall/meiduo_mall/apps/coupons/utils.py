


def skus_with_coupon(coupon):
    skus = coupon.skus.filter(is_launched=True)  # 多对多查出所有单独指定的sku
    category = coupon.category.all()  # 多对多查出所有分类
    for cat in category:  # 关键位置，取所有分类，要测试
        if cat.subs.all():  # 假如是第一级有分支
            for cat2 in cat.subs.all():  # 遍历第二级
                if cat2.subs.all():  # 第2级下还有第3级
                    for cat3 in cat2.subs.all():  # 遍历第3级
                        skus = skus | cat3.sku_set.filter(is_launched=True)
                else:
                    skus = skus | cat2.sku_set.filter(is_launched=True)
        else:
            skus = skus | cat.sku_set.filter(is_launched=True)  # 合并和去重，方式还可以使用chain
    print(f"优惠券id-{coupon.id}查到skus:{skus}")
    return skus
