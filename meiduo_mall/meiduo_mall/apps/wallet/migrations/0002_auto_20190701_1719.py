# Generated by Django 2.0 on 2019-07-01 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='share_code',
            field=models.IntegerField(verbose_name='分享码'),
        ),
    ]