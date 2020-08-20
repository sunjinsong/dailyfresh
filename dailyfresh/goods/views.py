from django.shortcuts import render,redirect
from .models import GoodsType,IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner,GoodsSKU
# Create your views here.
from django_redis import get_redis_connection
from order.models import OrderGoods
from django.core.paginator import Paginator
def index(request):

    #获取商品种类信息
    types=GoodsType.objects.all()

    #获取轮播信息
    goods_banners=IndexGoodsBanner.objects.all().order_by('index')

    #获取促销广告信息
    promotion_banners=IndexPromotionBanner.objects.all().order_by('index')

    #获取首页分类展示信息
    # type_goods_banners=IndexTypeGoodsBanner.objects.all()
    for type in types:
        image_banners=IndexTypeGoodsBanner.objects.filter(type=type,display_type=1).order_by('index')
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')
        type.image_banners=image_banners
        type.title_banners=title_banners

    #购物车商品的数量
    cart_count=0

    #判断用户是否登录
    user=request.user
    if user.is_authenticated:
        conn=get_redis_connection('default')
        cart_key='cart_%d'%user.id
        cart_count=conn.hlen(cart_key)

    context={
        'types':types,
        'goods_banners':goods_banners,
        'promotion_banners':promotion_banners,
        'cart_count':cart_count,
    }
    return render(request,'index.html',context=context)


def detail(request,goods_id):
    '''显示商品详情'''
    try:
        sku=GoodsSKU.objects.get(id=goods_id)
    except:
        return redirect('goods:index')
    #获取商品的分类信息
    types=GoodsType.objects.all()

    #获取商品的新品
    new_goods=GoodsSKU.objects.all().order_by('create_time')[:2]

    #获取评论
    comments=OrderGoods.objects.filter(sku=sku)[:10]

    #判断用户是否登录
    user=request.user
    cart_count=0
    if user.is_authenticated:
        conn=get_redis_connection('default')
        cart_key='cart_%d'%user.id
        cart_count=conn.hlen(cart_key)
        #添加用户的浏览记录
        conn = get_redis_connection('default')
        history_key='history_%d'%user.id
        #移除表中的goods_id
        conn.lrem(history_key,0,goods_id)
        #把goods_id插入到列表的左侧
        conn.lpush(history_key,goods_id)
        #只保存用户最新浏览的5条信息
        conn.ltrim(history_key,0,4)
    context={
        'sku':sku,
        'types':types,
        'new_goods':new_goods,
        'comments':comments,
        'cart_count':cart_count,
    }


    return render(request,'detail.html',context=context)


def ListModels(request,type_id,page):
    try:
        type=GoodsType.objects.get(id=type_id)
    except:
        return redirect('goods:index')

    #获取分类信息
    types=GoodsType.objects.all()



    #获取排列的方式  sort=default price hot
    sort=request.GET.get('sort','default')
    if sort=='default':
        skus=GoodsSKU.objects.filter(type=type).order_by('-id')
    elif sort=='price':
        skus=GoodsSKU.objects.filter(type=type).order_by('price')
    elif sort=='hot':
        skus=GoodsSKU.objects.filter(type=type).order_by('-sales')
    else:
        return redirect('goods:index')

    #分页
    paginator=Paginator(skus,10)
    #获取第page页的内容
    try:
        page=int(page)
    except:
        page=1
    if page>paginator.num_pages:
        page=1
    skus_page=paginator.page(page)

    #购物车数目
    cart_count=0
    user = request.user
    if user.is_authenticated:
        conn=get_redis_connection('default')
        cart_key='cart_%d'%user.id
        cart_count=conn.hlen(cart_key)

    #获取商品的新品
    new_goods=GoodsSKU.objects.all().order_by('-create_time')[:2]
    num_pages=paginator.num_pages
    if num_pages<5:
        pages=range(1,num_pages+1)
    elif page<=3:
        pages=range(1,6)
    elif num_pages-page<=2:
        pages=range(num_pages-4,num_pages+1)
    else:
        pages=range(page-1,page+3)

    #组织模板的上下文
    context={
        'type':type_id,
        'new_goods':new_goods,
        'cart_count':cart_count,
        'skus_page':skus_page,
        'new_goods':new_goods,
        'types':types,
        'pages':pages,
        'sort':sort,

    }
    return render(request,'list.html',context=context)