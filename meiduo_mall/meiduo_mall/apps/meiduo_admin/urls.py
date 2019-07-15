from django.urls import path, re_path
from rest_framework.routers import SimpleRouter
from rest_framework_jwt.views import obtain_jwt_token

from meiduo_admin.views.brand_views import BrandViewSet
from meiduo_admin.views.channels_views import ChannelViewSet, ChannelGroupView
from meiduo_admin.views.goods_views import GoodsViewSet
from meiduo_admin.views.home_views import HomeViewSet
from meiduo_admin.views.image_view import ImageViewSet
from meiduo_admin.views.options_views import OptionsViewSet
from meiduo_admin.views.order_views import OrderViewSet
from meiduo_admin.views.sku_views import SKUGoodsViewSet
from meiduo_admin.views.spec_views import SpecViewSet
from meiduo_admin.views.spu_views import ChannelCategoryView, SPUBrandView
from meiduo_admin.views.user_views import UserView

app_name = 'meiduo_admin'
urlpatterns = [
    # 登录
    path('authorizations/', obtain_jwt_token),
    # 用户管理
    path('users/', UserView.as_view()),
    # 规格表管理
    re_path(r'^goods/specs/$', SpecViewSet.as_view({"get": "list", "post": "create"})),
    re_path(r'^goods/specs/simple/$', SpecViewSet.as_view({"get": "simple"})),
    re_path(r'^goods/specs/(?P<pk>\d+)/$', SpecViewSet.as_view({"get": "retrieve",
                                                                "delete": "destroy",
                                                                "put": "update",
                                                                "patch": "partial_update"})),
    # 商品图片管理
    re_path(r'^skus/images/$', ImageViewSet.as_view({"get": "list", "post": "create"})),
    re_path(r'^skus/images/simple/$', ImageViewSet.as_view({"get": "simple"})),
    re_path(r'^skus/images/(?P<pk>\d+)/$', ImageViewSet.as_view({"get": "retrieve",
                                                                 "delete": "destroy",
                                                                 "put": "update",
                                                                 "patch": "partial_update"})),
    # 获得spu所属一级分类信息
    path('goods/channel/categories/', ChannelCategoryView.as_view()),
    # 获得spu所属二级或三级分类信息
    re_path(r'^goods/channel/categories/(?P<pk>\d+)/$', ChannelCategoryView.as_view()),
    # 获得spu所属的品牌信息
    path('goods/brands/simple/', SPUBrandView.as_view()),
    # 频道表管理
    re_path(r'^goods/channels/$', ChannelViewSet.as_view({"get": "list", "post": "create"})),
    re_path(r'^goods/channels/(?P<pk>\d+)/$', ChannelViewSet.as_view({"get": "retrieve",
                                                                      "delete": "destroy",
                                                                      "put": "update",
                                                                      "patch": "partial_update"})),
    # 获得新建频道可选一级分类
    path('goods/categories/', ChannelCategoryView.as_view()),
    path('goods/channel_types/', ChannelGroupView.as_view()),
    # 品牌管理
    re_path(r'^goods/brands/$', BrandViewSet.as_view({"get": "list", "post": "create"})),
    re_path(r'^goods/brands/(?P<pk>\d+)/$', BrandViewSet.as_view({"get": "retrieve",
                                                                      "delete": "destroy",
                                                                      "put": "update",
                                                                      "patch": "partial_update"})),

]

router = SimpleRouter()

router.register(prefix='statistical', viewset=HomeViewSet, base_name='home')
router.register(prefix='skus', viewset=SKUGoodsViewSet, base_name='skus')
# router.register(prefix='goods/specs', viewset=SpecViewSet, base_name='specs')
router.register(prefix='goods', viewset=GoodsViewSet, base_name='good')

router.register(prefix='specs/options', viewset=OptionsViewSet, base_name='options')
router.register(prefix='orders', viewset=OrderViewSet, base_name='orders')
urlpatterns += router.urls
