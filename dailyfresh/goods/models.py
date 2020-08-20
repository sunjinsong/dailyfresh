from django.db import models
# Create your models here.
# from db.base_model import BaseModel
from tinymce.models import HTMLField
class BaseModel(models.Model):
    create_time=models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    update_time=models.DateTimeField(auto_now=True,verbose_name='更新时间')
    is_delete=models.BooleanField(default=False,verbose_name='删除标记')

    class Meta:
        abstract=True
class GoodsType(BaseModel):
    name=models.CharField(max_length=20,verbose_name='种类名字')
    logo=models.CharField(max_length=20,verbose_name='标识')
    image=models.ImageField(upload_to='type',verbose_name='商品种类图片')

    class Meta:
        db_table='df_goods_type'
        verbose_name='商品种类'
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.name


class Goods(BaseModel):
    name=models.CharField(max_length=20,verbose_name='商品的SPU名字')
    detail=HTMLField(blank=True,verbose_name='商品详情')
    class Meta:
        db_table='df_goods'
        verbose_name='商品SPU'
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.name

class GoodsSKU(BaseModel):
    status_choices=(
        (0,'下线'),
        (1,'上线')
    )
    type=models.ForeignKey(GoodsType,verbose_name='商品种类',on_delete=models.CASCADE)
    goods=models.ForeignKey(Goods,verbose_name='商品SPU',on_delete=models.CASCADE)
    name=models.CharField(max_length=20,verbose_name='商品名字')
    desc=models.CharField(max_length=256,verbose_name='商品简介')
    price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name='价格')
    unite=models.CharField(max_length=20,verbose_name='商品单位')
    image=models.ImageField(upload_to='goods',verbose_name='商品图片')
    stock=models.IntegerField(default=1,verbose_name='商品库存')
    sales=models.IntegerField(default=0,verbose_name='商品销量')
    status=models.SmallIntegerField(default=1,choices=status_choices,verbose_name='商品状态')

    class Meta:
        db_table='df_goods_sku'
        verbose_name='商品SKU'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.name


class GoodsImage(BaseModel):
    sku=models.ForeignKey(GoodsSKU,verbose_name='商品的sku',on_delete=models.CASCADE)
    image=models.ImageField(upload_to='goods',verbose_name='商品图片')

    class Meta:
        db_table='df_goods_image'
        verbose_name='商品图片'
        verbose_name_plural=verbose_name


class IndexGoodsBanner(BaseModel):
    sku=models.ForeignKey(GoodsSKU,verbose_name='商品SKU',on_delete=models.CASCADE)
    image=models.ImageField(upload_to='banner',verbose_name='轮播图片')
    index=models.SmallIntegerField(default=0,verbose_name='展示顺序')

    class Meta:
        db_table='df_index_banner'
        verbose_name='首页轮播商品'
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.sku.name


class IndexPromotionBanner(BaseModel):
    name=models.CharField(max_length=20,verbose_name='活动名称')
    url=models.URLField(verbose_name='活动链接')
    image=models.ImageField(upload_to='banner',verbose_name='活动图片')
    index=models.SmallIntegerField(default=0,verbose_name='展示顺序')

    class Meta:
        db_table='df_index_promotion'
        verbose_name='主页促销活动'
        verbose_name_plural=verbose_name
    def __str__(self):
        return self.name


class IndexTypeGoodsBanner(BaseModel):
    DISPLAY_TYPE_CHOICES=(
        (0,'标题'),
        (1,'图片'),
    )

    type=models.ForeignKey(GoodsType,verbose_name='商品类型',on_delete=models.CASCADE)
    sku=models.ForeignKey(GoodsSKU,verbose_name='商品SKU',on_delete=models.CASCADE)
    display_type=models.SmallIntegerField(default=1,choices=DISPLAY_TYPE_CHOICES,verbose_name='展示类型')
    index=models.SmallIntegerField(default=0,verbose_name='展示顺序')
    class Meta:
        db_table='df_index_goods'
        verbose_name='主页分类展示商品'
        verbose_name_plural=verbose_name

    def __str__(self):
        return self.sku.name
