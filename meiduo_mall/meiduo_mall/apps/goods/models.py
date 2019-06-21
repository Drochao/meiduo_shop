from django.db import models

from meiduo_mall.utils.models import BaseModel


class GoodsCategory(BaseModel):
    """商品类别"""
    name = models.CharField('名称', max_length=10)
    parent = models.ForeignKey('self', related_name='subs', null=True, blank=True, on_delete=models.CASCADE, verbose_name='父类别')

    class Meta:
        db_table = 'tb_goods_category'
        verbose_name = '商品类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class GoodsChannelGroup(BaseModel):
    """商品频道组"""
    name = models.CharField('频道组名', max_length=20)

    class Meta:
        db_table = 'tb_channel_group'
        verbose_name = '商品频道组'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class GoodsChannel(BaseModel):
    """商品频道"""
    group = models.ForeignKey(GoodsChannelGroup, verbose_name='频道组名', on_delete=models.CASCADE)
    category = models.ForeignKey(GoodsCategory, on_delete=models.CASCADE, verbose_name='顶级商品类别')
    url = models.CharField('频道页面链接', max_length=50)
    sequence = models.IntegerField('组内顺序')

    class Meta:
        db_table = 'tb_goods_channel'
        verbose_name = '商品频道'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.category.name


class Brand(BaseModel):
    """品牌"""
    name = models.CharField('名称', max_length=20)
    logo = models.ImageField('Logo图片')
    first_letter = models.CharField('品牌首字母', max_length=1)

    class Meta:
        db_table = 'tb_brand'
        verbose_name = '品牌'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SPU(BaseModel):
    """商品SPU"""
    name = models.CharField('名称', max_length=50)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, verbose_name='品牌')
    category1 = models.ForeignKey(GoodsCategory, on_delete=models.PROTECT, related_name='cat1_spu', verbose_name='一级类别')
    category2 = models.ForeignKey(GoodsCategory, on_delete=models.PROTECT, related_name='cat2_spu', verbose_name='二级类别')
    category3 = models.ForeignKey(GoodsCategory, on_delete=models.PROTECT, related_name='cat3_spu', verbose_name='三级类别')
    sales = models.IntegerField('销量', default=0)
    comments = models.IntegerField('评价数', default=0)
    desc_detail = models.TextField('详细介绍', default='')
    desc_pack = models.TextField('包装信息', default='')
    desc_service = models.TextField('售后服务', default='')

    class Meta:
        db_table = 'tb_spu'
        verbose_name = '商品SPU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class SKU(BaseModel):
    """商品SKU"""
    name = models.CharField('名称', max_length=50)
    caption = models.CharField('副标题', max_length=100)
    spu = models.ForeignKey(SPU, on_delete=models.CASCADE, verbose_name='商品')
    category = models.ForeignKey(GoodsCategory, on_delete=models.PROTECT, verbose_name='从属类别')
    price = models.DecimalField('单价', max_digits=10, decimal_places=2)
    cost_price = models.DecimalField('进价', max_digits=10, decimal_places=2)
    market_price = models.DecimalField('市场价', max_digits=10, decimal_places=2)
    stock = models.IntegerField('库存', default=0)
    sales = models.IntegerField('销量', default=0)
    comments = models.IntegerField('评价数', default=0)
    is_launched = models.BooleanField('是否上架销售', default=True)
    default_image = models.ImageField('默认图片', max_length=200, default='', null=True, blank=True)

    class Meta:
        db_table = 'tb_sku'
        verbose_name = '商品SKU'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s' % (self.id, self.name)


class SKUImage(BaseModel):
    """SKU图片"""
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE, verbose_name='sku')
    image = models.ImageField(verbose_name='图片')

    class Meta:
        db_table = 'tb_sku_image'
        verbose_name = 'SKU图片'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s %s' % (self.sku.name, self.id)


class SPUSpecification(BaseModel):
    """商品SPU规格"""
    spu = models.ForeignKey(SPU, on_delete=models.CASCADE, related_name='specs', verbose_name='商品SPU')
    name = models.CharField('规格名称', max_length=20)

    class Meta:
        db_table = 'tb_spu_specification'
        verbose_name = '商品SPU规格'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s' % (self.spu.name, self.name)


class SpecificationOption(BaseModel):
    """规格选项"""
    spec = models.ForeignKey(SPUSpecification, related_name='options', on_delete=models.CASCADE, verbose_name='规格')
    value = models.CharField('选项值', max_length=20)

    class Meta:
        db_table = 'tb_specification_option'
        verbose_name = '规格选项'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s - %s' % (self.spec, self.value)


class SKUSpecification(BaseModel):
    """SKU具体规格"""
    sku = models.ForeignKey(SKU, related_name='specs', on_delete=models.CASCADE, verbose_name='sku')
    spec = models.ForeignKey(SPUSpecification, on_delete=models.PROTECT, verbose_name='规格名称')
    option = models.ForeignKey(SpecificationOption, on_delete=models.PROTECT, verbose_name='规格值')

    class Meta:
        db_table = 'tb_sku_specification'
        verbose_name = 'SKU规格'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.sku}: {self.spec.name} - {self.option.value}'