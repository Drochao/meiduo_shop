from django.urls import path, re_path

from orders import views

app_name = 'orders'

urlpatterns = [
    path('settlement/', views.OrderSettlementView.as_view(), name='settlement'),
    path('commit/', views.OrderCommitView.as_view(), name='commit'),
    path('success/', views.OrderSuccessView.as_view(), name='success'),
    path('comments/', views.CommentView.as_view(), name='comment'),
    re_path(r'^info/(?P<page_num>\d+)/$', views.OrderInfoView.as_view(), name='info'),
]
