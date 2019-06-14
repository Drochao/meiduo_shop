from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    """自定义用户模型类"""
    mobile = models.CharField('手机号', max_length=11, unique=True)
    email_active = models.BooleanField('邮箱验证状态', default=False)

    class Meta(AbstractUser.Meta):
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
