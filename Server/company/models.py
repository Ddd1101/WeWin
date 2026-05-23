from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='企业名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='企业编号')
    address = models.CharField(max_length=500, blank=True, null=True, verbose_name='企业地址')
    contact_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='联系人姓名')
    contact_phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='联系电话')
    is_active = models.BooleanField(default=True, verbose_name='是否可用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'company'
        verbose_name = '企业'
        verbose_name_plural = '企业'

    def __str__(self):
        return self.name
