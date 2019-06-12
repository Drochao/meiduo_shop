
from django.urls import path, re_path

from meiduo_mall.apps.users import views

app_name = 'users'

urlpatterns = [
    path('register/', views.Register.as_view(), name="register"),
    re_path(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    re_path(r'^mobiles/(?P<mobile>1[345789]\d{9})/count/$', views.MobileCountView.as_view()),
]
