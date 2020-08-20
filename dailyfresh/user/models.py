from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# from db.base_model import BaseModel
# Create your models here.
class BaseModel(models.Model):
    create_time=models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    update_time=models.DateTimeField(auto_now=True,verbose_name='更新时间')
    is_delete=models.BooleanField(default=False,verbose_name='删除标记')

    class Meta:
        abstract=True
class User(AbstractUser,BaseModel):
    class Meta:
        db_table='df_user'
        verbose_name='用户'
        verbose_name_plural=verbose_name
class AddressManager(models.Manager):
    def get_default_address(self,user):
        try:
            addr=AddressBaseModel.objects.get(user=user,is_default=True)
        except:
            addr=None
        return addr

class AddressBaseModel(models.Model):
    user=models.ForeignKey('User',verbose_name='所属用户',on_delete=models.CASCADE)
    recever=models.CharField(max_length=20,verbose_name='接收人')
    addr=models.CharField(max_length=256,verbose_name='接收地址')
    zip_code=models.CharField(max_length=10,verbose_name='邮政编码')
    phone=models.CharField(max_length=11,verbose_name='联系方式')
    is_default=models.BooleanField(default=False,verbose_name='默认地址')
    objects=AddressManager()
    class Meta:
        db_table='df_address'
        verbose_name='地址'
        verbose_name_plural=verbose_name