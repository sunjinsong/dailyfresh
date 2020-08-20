from django.shortcuts import render,redirect,reverse
from django.http import HttpResponse
# Create your views here.
from .models import User
from django.http import HttpResponse
from django.conf import settings
from itsdangerous import SignatureExpired
from django.core.mail import send_mail
from itsdangerous import  TimedJSONWebSignatureSerializer as Serializer
from django.contrib.auth import authenticate,logout,login
from django.contrib.auth.decorators import login_required
from .models import AddressBaseModel
from django_redis import get_redis_connection
from goods.models import GoodsSKU
from order.models import OrderInfo,OrderGoods
from django.core.paginator import Paginator
def register(request):
    if request.method=='GET':
        return render(request,'register.html')
    else:
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 判断数据是否完整
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 判断邮箱是否合法

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同一协议'})

        # 进行业务处理  用户的注册
        if User.objects.filter(username=username):
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        user = User.objects.create_user(username, email, password)
        user.is_active = 0          #设置为未激活状态
        user.save()
        #发送激活链接
        #生成链接
        serializer=Serializer(settings.SECRET_KEY,3600)     #创建一个对象
        info={'confirm':user.id}
        token=serializer.dumps(info).decode()       #加密
        #发送邮件
        subject='天天生鲜欢迎信息'
        message=''
        sender=settings.EMAIL_HOST_USER
        receiver=[email]
        html_message="<h1>%s,欢迎你成为天天生鲜的会员</h1>请点击以下的链接来激活账户<br><a href='http://127.0.0.1/user/active/%s/'>127.0.0.1/user/active/%s</a>"%(user.username,token,token)
        send_mail(subject,message,sender,receiver,html_message=html_message)
        # 跳转到首页
        return redirect('user:login')

#激活用户
def active(request,token):
    serializer = Serializer(settings.SECRET_KEY, 3600)
    try:
        info=serializer.loads(token)
        id=info['confirm']
        user=User.objects.get(id=id)
        user.is_active=1
        user.save()

        return redirect('user:login')
    except:
        return HttpResponse('激活链接已经过期')

def loginview(request):
    if request.method=='POST':
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '信息不完整'})

        user = authenticate(username=username, password=password)
        if user:  # 表示验证成功
            if user.is_active:  # 表示已经激活
                login(request, user)
                remeber = request.POST.get('remeber')
                next_url = request.GET.get('next', reverse('goods:index'))      #当没有登录的用户访问一个网页时会自动跳转到这个url  并且传递来了本来访问的地址  next
                respone = redirect(next_url)
                if remeber == 'on':             #表示记住用户
                    respone.set_cookie('username', username, max_age=7 * 24 * 3600)
                else:
                    respone.delete_cookie('username')
                return respone
            else:
                return render(request, 'login.html', {'errmsg': '用户名没有激活'})
        else:  # 表示验证失败
            return render(request, 'login.html', {'errmsg': '用户名或者密码错误'})


    else:
        # 判断是否记住了账户
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request, 'login.html', {'checked': checked, 'username': username})

def UserLogout(request):
    logout(request)
    return redirect('goods:index')
@login_required
def UserInfo(request):
    #page是用来高亮显示的标志
    #request.user会返回已经够登录的用户model
    #request.user.is_autenticated()如果用户已经登录会返回True
    #request.user会作为user自动传递到模板
    user=request.user
    addr=AddressBaseModel.objects.get_default_address(user)
    con=get_redis_connection('default')
    history_key='history_%d'%user.id
    sku_ids=con.lrange(history_key,0,4)
    goods_li=[]
    for id in sku_ids:
        goods=GoodsSKU.objects.get(id=id)
        goods_li.append(goods)
    context={
        'goods_li':goods_li,
        'page':'info',
        'addr':addr
    }
    return render(request,'user_center_info.html',context=context)
@login_required
def UserOrder(request,page):
    user=request.user
    #获取用户所有的订单
    orders=OrderInfo.objects.filter(user=user)
    #获取每个订单的商品信息

    for order in orders:
        #每个订单的所有商品
        order_skus=OrderGoods.objects.filter(order_id=order.order_id)
        #遍历一个订单的所有商品
        for order_sku in order_skus:
            #计算小计
            amount=order_sku.count*order_sku.price
            order_sku.amount=amount     #动态增加属性
        order.order_skus=order_skus

    #分页
    paginator=Paginator(orders,10)
    #获取第page页的内容
    try:
        page=int(page)
    except:
        page=1
    if page>paginator.num_pages:
        page=1
    order_page=paginator.page(page)

    num_pages=paginator.num_pages
    if num_pages<5:
        pages=range(1,num_pages+1)
    elif page<=3:
        pages=range(1,6)
    elif num_pages-page<=2:
        pages=range(num_pages-4,num_pages+1)
    else:
        pages=range(page-1,page+3)

    context={
        'order_page':order_page,
        'pages':pages,
        'page':'order',
    }
    return render(request,'user_center_order.html',context=context)
@login_required
def UserSite(request):
    if request.method=='GET':
        user=request.user
        # #获取默认地址
        # try:
        #     addr=AddressBaseModel.objects.get(user=user,is_default=True)
        # except:
        #     addr=None
        addr=AddressBaseModel.objects.get_default_address(user)
        return render(request,'user_center_site.html',{'page':'site','addr':addr,'user':user})
    else:
        #获取数据
        receiver=request.POST.get('receiver')
        addr=request.POST.get('addr')
        zip_code=request.POST.get('zip_code')
        phone=request.POST.get('phone')
        #验证数据
        if not all([receiver,addr,phone]):
            return render(request,'user_center_site.html',{'errmsg':'数据不完整'})
        #验证手机号 地址 。。。

        #处理数据
        user=request.user   #获取用户
        # try:
        #     default_addr=AddressBaseModel.objects.get(user=user,is_default=True)#存在默认地址
        # except:
        #     default_addr=None   #不存在默认地址
        default_addr = AddressBaseModel.objects.get_default_address(user)
        if default_addr:
            AddressBaseModel.objects.create(user=user,recever=receiver,addr=addr,phone=phone,is_default=False)
        else:
            AddressBaseModel.objects.create(user=user,recever=receiver,addr=addr,phone=phone,is_default=True)

        #返回结果

        return redirect('user:usersite')


# def register_handle(request):
#     username=request.POST.get('user_name')
#     password=request.POST.get('pwd')
#     email=request.POST.get('email')
#     allow=request.POST.get('allow')
#     #判断数据是否完整
#     if not all([username,password,email]):
#         return render(request,'register.html',{'errmsg':'数据不完整'})
#
#     #判断邮箱是否合法
#
#     if allow!='on':
#         return render(request,'register.html',{'errmsg':'请同一协议'})
#
#     #进行业务处理  用户的注册
#     if User.objects.filter(username=username):
#         return render(request,'register.html',{'errmsg':'用户名已存在'})
#     user=User.objects.create_user(username,email,password)
#     user.is_active=0
#     user.save()
#     #跳转到首页
#     return redirect('goods:index')

