from django.urls import path
from . import views
urlpatterns = [
    path('orderplace/',views.OrderPlace,name='orderplace'),
    path('commitcart/',views.CommitOrder,name='commitorder'),
]