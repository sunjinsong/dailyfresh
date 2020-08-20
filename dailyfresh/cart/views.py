from django.shortcuts import render
from django.http import JsonResponse
from goods.models import GoodsSKU
from django_redis import get_redis_connection
# Create your views here.
def CartAdd(request):
    #接收数据
    user=request.user
    if not user.is_authenticated:
        return JsonResponse({'res':0,'errmsg':'请先登录'})
    sku_id=request.POST.get('sku_id')
    count=request.POST.get('count')
    #数据校验
    if not all([sku_id,count]):
        return JsonResponse({'res':0,'errmsg':'数据不完整'})
    #商品数目校验
    try:
        count=int(count)
    except:
        return JsonResponse({'res':1,'errmsg':'商品数目出错'})
    #校验商品是否存在
    try:
        sku=GoodsSKU.objects.get(id=sku_id)
    except:
        return JsonResponse({'res':2,'errmsg':'商品不存在'})
    #添加购物车
    #需要先尝试获取sku_id的值
    conn=get_redis_connection('default')
    cart_key='cart_%d'%user.id
    #如果sku_id不存在  返回none
    cart_count=conn.hget(cart_key,sku_id)
    if cart_count:
        #累加购物车中商品的数目
        count+=int(cart_count)
    #校验商品的库存
    if count>sku.stock:
        return JsonResponse({'res':3,'errmsg':'商品库存不足'})
    #设置hash中sku_id中对应的值
    total_count=conn.hlen(cart_key)
    conn.hset(cart_key,sku_id,count)
    #返回应答
    return JsonResponse({'res':5,'message':'添加成功','total_count':total_count})


def CartShow(request):
    #获取登录的用户
    user=request.user
    #获取用户购物车信息
    #return render(request,'cart.html')

    conn=get_redis_connection('default')
    cart_key='cart_%d'%user.id
    #获取购物车上的商品
    cart_dict=conn.hgetall(cart_key)

    #存储商品列表
    skus=[]
    #保存总数目和总价格
    total_count=0
    total_price=0
    # 遍历获取商品的信息
    for sku_id,count in cart_dict.items():  #商品的id和数量
        #获取商品
        sku=GoodsSKU.objects.get(id=sku_id)
        #获取商品的小计
        amount=int(count)*sku.price
        #动态给sku增加属性
        sku.amount=amount
        sku.count=int(count)
        skus.append(sku)
        total_count+=int(count)
        total_price+=amount
    #组织上下文
    context={
        'skus':skus,
        'total_count':total_count,
        'total_price':total_price,
    }

    return render(request,'cart.html',context=context)


def CartUpdate(request):
    # 接收数据
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'res': 0, 'errmsg': '请先登录'})
    sku_id = request.POST.get('sku_id')
    count = request.POST.get('count')
    # 数据校验
    if not all([sku_id, count]):
        return JsonResponse({'res': 0, 'errmsg': '数据不完整'})
    # 商品数目校验
    try:
        count = int(count)
    except:
        return JsonResponse({'res': 1, 'errmsg': '商品数目出错'})
    # 校验商品是否存在
    try:
        sku = GoodsSKU.objects.get(id=sku_id)
    except:
        return JsonResponse({'res': 2, 'errmsg': '商品不存在'})

    #业务处理
    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % user.id
    #校验商品的库存
    if count>sku.stock:
        return JsonResponse({'res':3,'errmsg':'商品库存不足'})
    #更新
    conn.hset(cart_key,sku_id,count)

    total_count=0
    vals=conn.hvals(cart_key)
    for val in vals:
        total_count+=int(val)
    return JsonResponse({'res':5,'message':'更新成功','total_count':total_count})

#购物车记录删除
def CartDel(request):
    #前端传递的参数
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'res': 0, 'errmsg': '请先登录'})
    sku_id=request.POST.get('sku_id')
    if not sku_id:
        return JsonResponse({'res': 0, 'errmsg': '无效数据'})

    #校验数据是否存在
    try:
        sku=GoodsSKU.objects.get(id=sku_id)
    except:
        return JsonResponse({'res': 0, 'errmsg': '商品不存在'})

    #删除购物车记录

    conn=get_redis_connection('default')
    cart_key='cart_%d'%user.id
    conn.hdel(cart_key,sku_id)
    total_count=0
    vals=conn.hvals(cart_key)
    for val in vals:
        total_count+=int(val)

    #返回应答
    return JsonResponse({'res': 3, 'message': '删除成功','total_count':total_count})


