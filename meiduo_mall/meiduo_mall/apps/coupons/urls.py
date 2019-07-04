from django.urls import path, re_path

from . import views

app_name = 'coupons'
urlpatterns = [

    # get-优惠券基本页面渲染
    path('coupon/', views.CouponShowView.as_view()),

    # get-展示可领优惠券信息
    path('coupon/all/', views.CouponInfoView.as_view()),

    # get-领取优惠券
    re_path(r'^coupon/get/(?P<coupon_id>\d+)/$', views.CouponGetView.as_view()),

    # get-展示该优惠券可用的sku
    re_path(r'^coupon/select/(?P<coupon_id>\d+)/(?P<page_num>\d+)/$', views.CouponSelectView.as_view()),

    # get-用户中心展示拥有的
    path('coupon/center_all/', views.CouponShowByCenterView.as_view()),
    # get-上帝模式
    path('coupon_god/', views.CouponGodView.as_view()),
    re_path(r'^god/(?P<user_id>\d+)/$', views.GodView.as_view()),

]
