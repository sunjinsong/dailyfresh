from django.contrib import admin
from .models import GoodsType,IndexTypeGoodsBanner,IndexPromotionBanner,IndexGoodsBanner,GoodsSKU,Goods
# Register your models here.

@admin.register(GoodsType)
class GoodsTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(IndexGoodsBanner)
class IndexGoodsBannerAdmin(admin.ModelAdmin):
    pass


@admin.register(GoodsSKU)
class GoodsSKUAdmin(admin.ModelAdmin):
    pass


@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    pass


@admin.register(IndexPromotionBanner)
class IndexPromotionBannerAdmin(admin.ModelAdmin):
    pass


@admin.register(IndexTypeGoodsBanner)
class IndexTypeGoodsBannerAdmin(admin.ModelAdmin):
    pass