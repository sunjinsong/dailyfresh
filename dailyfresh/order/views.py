from django.shortcuts import render,redirect
# Create your views here.
from goods.models import GoodsSKU
from django_redis import get_redis_connection
from user.models import AddressBaseModel
from django.http import JsonResponse
from .models import OrderInfo,OrderGoods
from datetime import datetime
from django.db import transaction
#提交订单显示
def OrderPlace(request):
    #获取参数
    sku_ids=request.POST.getlist('sku_ids')
    #校验参数
    if not sku_ids:
        #跳转到购物车
        return redirect('cart:show')
    #获取用户
    user=request.user
    cart_key='cart_%d'%user.id
    conn=get_redis_connection('default')
    #遍历sku_ids  获取商品
    skus=[]
    total_count=0
    total_amount=0  #分别保存总价格和总件数
    for sku_id in sku_ids:
        #根据id获取商品
        sku=GoodsSKU.objects.get(id=sku_id)
        count=conn.hget(cart_key,sku_id)
        amount=sku.price*int(count)

        #动态增加属性
        sku.count=int(count)
        sku.amount=amount
        total_count+=int(count)
        total_amount+=int(amount)
        skus.append(sku)
    #运费
    transit_price=10
    #实付款
    total_pay=total_amount+transit_price

    #收获地址
    addrs=AddressBaseModel.objects.filter(user=user)
    sku_ids=','.join(sku_ids)
    #组织上下文
    context={
        'total_count':total_count,
        'total_amount':total_amount,
        'total_pay':total_pay,
        'transit_price':transit_price,
        'skus':skus,
        'addrs':addrs,
        'sku_ids':sku_ids,
    }
    return render(request,'place_order.html',context=context)


#提交订单
@transaction.atomic
def CommitOrder(request):
    #判断用户是否登录
    user=request.user

    if not user.is_authenticated:
        return JsonResponse({'res':0,'errmsg':'用户没有登录'})

    #接收参数

    addr_id=request.POST.get('addr_id')
    pay_method=request.POST.get('pay_method')
    sku_ids=request.POST.get('sku_ids')

    #校验完整性
    if not all([addr_id,pay_method,sku_ids]):
        return JsonResponse({'res':0,'errmsg':'数据不完整'})

    #校验支付方式
    # if pay_method not in OrderInfo.PAY_METHOD_CHOICES:
    #     return JsonResponse({'res':0,'errmsg':'支付方式不合法'})

    #校验支付方式

    try:
        addr=AddressBaseModel.objects.get(id=addr_id)
    except:
        return JsonResponse({'res':0,'errmsg':'地址不合法'})

    #创建订单
    #订单id  使用年月日时间+用户id来作为id
    order_id=datetime.now().strftime('%Y%m%d%H%M%S')+str(user.id)
    #运费
    transit_price=10
    #总数目和总金额  默认值
    total_count=0
    total_price=0


    #添加记录
    order=OrderInfo.objects.create(order_id=order_id,user=user,address=addr,pay_method=pay_method,
                        total_count=total_count ,total_price=total_price,
                        transit_price=transit_price,
                             )

    #添加商品的id
    sku_ids=sku_ids.split(',')
    conn=get_redis_connection('default')
    cart_key='cart_%d'%user.id
    for sku_id in sku_ids:
        #获取商品信息
        try:
            sku=GoodsSKU.objects.get(id=sku_id)
        except:
            return JsonResponse({'res':0,'errmsg':'商品不存在'})

        #从redis中获取用户所要购买的商品数量
        count=conn.hget(cart_key,sku_id)
        # 判断库存
        if int(count)>sku.stock:
            return JsonResponse({'res':0,'errmsg':'库存不足'})
        #向OrderGoods中添加记录
        OrderGoods.objects.create(order=order,sku=sku,count=count,price=sku.price)
        #更新商品的库存和销量
        sku.stock-=int(count)
        sku.sales+=int(count)
        sku.save()

        #计算总数量和总价格
        amount=sku.price*int(count)
        total_price+=amount
        total_count+=int(count)

    #更新订单的总数量和总价格
    order.total_count=total_count
    order.total_price=total_price
    order.save()

    #清除用户购物车的记录
    conn.hdel(cart_key,*sku_ids)

    #返回订单
    return JsonResponse({'res':5,'message':'创建成功'})
