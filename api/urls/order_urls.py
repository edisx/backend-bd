from django.urls import path
from api.views import order_views as views

urlpatterns = [

    path('', views.getOrders, name='orders'),
    path('add/', views.addOrder, name='orders-add'),
    path('myorders/', views.getMyOrders, name='myorders'),
    
    path('<str:pk>/shipped/', views.updateOrderToShipped, name='order-shipped'),
    path('<str:pk>/unshipped/', views.resetOrderToUnshipped, name='order-unshipped'),
    path('<str:pk>/deliver/', views.updateOrderToDelivered, name='order-delivered'),
    path('<str:pk>/undeliver/', views.resetOrderToUndelivered, name='order-undelivered'),
    
    path('<str:pk>/', views.getOrderById, name='user-order'),
    path('<str:pk>/pay/', views.updateOrderToPaid, name='pay')
]

