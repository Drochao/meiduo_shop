from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
from meiduo_mall.utils.models import BaseModel


class User(AbstractUser):
    """自定义用户模型类"""
    mobile = models.CharField('手机号', max_length=11, unique=True)
    email_active = models.BooleanField('邮箱验证状态', default=False)
    default_address = models.ForeignKey('Address', related_name='users',
                                        null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name='默认地址')

    class Meta(AbstractUser.Meta):
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Address(BaseModel):
    """用户地址"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField('地址名称', max_length=20)
    receiver = models.CharField('收货人', max_length=20)
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')
    place = models.CharField('地址', max_length=50)
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField('固定电话', max_length=20, null=True, blank=True, default='')
    email = models.CharField('电子邮箱', max_length=30, null=True, blank=True, default='')
    is_deleted = models.BooleanField('逻辑删除', default=False)

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']