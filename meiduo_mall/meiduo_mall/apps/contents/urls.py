from django.urls import path, re_path

from meiduo_mall.apps.contents import views

app_name = 'contents'

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path("weather/", views.GetWeatherView.as_view()),  # 自定义拼接首页天气栏格式
]
