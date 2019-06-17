# Create your models here.
from django.db import models

from meiduo_mall.utils.models import BaseModel


class ContentCategory(BaseModel):
    """广告内容类别"""
    name = models.CharField('名称', max_length=50)
    key = models.CharField('类别键名', max_length=50)

    class Meta:
        db_table = 'tb_content_category'
        verbose_name = '广告内容类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Content(BaseModel):
    """广告内容"""
    category = models.ForeignKey(ContentCategory, on_delete=models.PROTECT, verbose_name='类别')
    title = models.CharField('标题', max_length=100)
    url = models.CharField('内容链接', max_length=300)
    image = models.ImageField('图片', null=True, blank=True)
    text = models.TextField('内容', null=True, blank=True)
    sequence = models.IntegerField('排序')
    status = models.BooleanField('是否展示', default=True)

    class Meta:
        db_table = 'tb_content'
        verbose_name = '广告内容'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.category.name + ': ' + self.title