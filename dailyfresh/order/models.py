from django.db import models
# from db.base_model import BaseModel
# Create your models here.
class BaseModel(models.Model):
    create_time=models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    update_time=models.DateTimeField(auto_now=True,verbose_name='更新时间')
    is_delete=models.BooleanField(default=False,verbose_name='删除标记')

    class Meta:
        abstract=True
class OrderInfo(BaseModel):
    PAY_METHOD_CHOICES=(
        ('1','货到付款'),
        ('2','微信支付'),
        ('3','支付宝'),
        ('4','银联支付'),
    )

    ORDER_STATUS_CHOICES=(
        (1,'待支付'),
        (2,'代发货'),
        (3,'待收货'),
        (4,'待评价'),
        (5,'已完成'),
    )

    order_id=models.CharField(max_length=128,primary_key=True,verbose_name='订单id')
    user=models.ForeignKey('user.User',verbose_name='用户',on_delete=models.CASCADE)
    address=models.ForeignKey('user.AddressBaseModel',verbose_name='地址',on_delete=models.CASCADE)
    pay_method=models.SmallIntegerField(choices=PAY_METHOD_CHOICES,verbose_name='支付方式')
    total_count=models.IntegerField(default=1,verbose_name='商品数量')
    total_price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='全部金额')
    transit_price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='运费')
    order_status=models.SmallIntegerField(choices=ORDER_STATUS_CHOICES,verbose_name='订单状态',default=1)
    order_no=models.CharField(max_length=128,verbose_name='支付编号')
    class Meta:
        db_table='df_order_info'
        verbose_name='订单'
        verbose_name_plural=verbose_name
        # app_label='user'

class OrderGoods(BaseModel):
    order=models.ForeignKey(OrderInfo,verbose_name='订单',on_delete=models.CASCADE)
    sku=models.ForeignKey('goods.GoodsSKU',verbose_name='商品SKU',on_delete=models.CASCADE)
    count=models.IntegerField(default=1,verbose_name='商品数目')
    price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='商品数目')
    comment=models.CharField(max_length=256,verbose_name='评论')
    class Meta:
        db_table='df_order_goods'
        verbose_name='订单商品'
        verbose_name_plural=verbose_name


