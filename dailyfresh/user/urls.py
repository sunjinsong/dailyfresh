from django.urls import path
from . import views
urlpatterns=[
    path('register/',views.register,name='register'),
    # path('register_handle/',views.register_handle,name='register_handle'),
    path('active/<str:token>',views.active,name='active'),
    path('login/',views.loginview,name='login'),
    path('userinfo/',views.UserInfo,name='userinfo'),
    path('userorder/<int:page>/', views.UserOrder, name='userorder'),
    path('usersite/', views.UserSite, name='usersite'),
    path('logout/',views.UserLogout,name='logout'),
]