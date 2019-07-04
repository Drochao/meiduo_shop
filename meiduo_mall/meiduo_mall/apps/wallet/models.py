from django.db import models

from users.models import User


class Wallet(models.Model):
    """钱包"""
    balance = models.DecimalField('余额', max_digits=10, decimal_places=2)
    share_code = models.IntegerField('分享码')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="用户")

    class Meta:
        db_table = 'tb_wallet'
        verbose_name = '钱包'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s' % (self.id, self.id)
