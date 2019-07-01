from django.urls import path, re_path

from meiduo_mall.apps.goods import views

app_name = 'goods'

urlpatterns = [
    re_path(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view(), name="list"),
    re_path(r'^hot/(?P<category_id>\d+)/$', views.HotGoodsView.as_view()),
    # 商品详情
    re_path(r'^detail/(?P<sku_id>\d+)/$', views.DetailView.as_view()),
    re_path(r'^visit/(?P<category_id>\d+)/$', views.DetailVisitView.as_view()),
    # re_path(r'^comments/(?P<sku_id>\d+)/$', views.ShowCommentView.as_view()),
]
