from django.urls import path, re_path

from orders import views

app_name = 'orders'

urlpatterns = [
    path('orders/settlement/', views.OrderSettlementView.as_view()),
    path('orders/commit/', views.OrderCommitView.as_view()),
    path('orders/success/', views.OrderSuccessView.as_view()),
]
