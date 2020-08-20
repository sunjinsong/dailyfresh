from django.urls import path
from . import views
urlpatterns=[
    path('',views.index,name='index'),  #首页
    path('detail/<int:goods_id>/',views.detail,name='detail'),
    path('list/<int:type_id>/<int:page>/', views.ListModels, name='list'),

]