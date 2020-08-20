from django.urls import path
from . import views
urlpatterns = [
    path('add/',views.CartAdd,name='add'),
    path('cart/',views.CartShow,name='cartshow'),
    path('cartupdate/',views.CartUpdate,name='cartupdate'),
    path('cartdel/',views.CartDel,name='cartdel'),
]