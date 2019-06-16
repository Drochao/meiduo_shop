from django.urls import path, re_path

from meiduo_mall.apps.users import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name="register"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('info/', views.UserInfoView.as_view(), name="info"),
    path('emails/', views.EmailView.as_view(), name="emails"),
    path('addresses/', views.AddressView.as_view(), name="addresses"),
    path('password/', views.ChangePasswordView.as_view(), name="password"),
    path('addresses/create/', views.CreateAddressView.as_view()),
    re_path(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UsernameCountView.as_view()),
    re_path(r'^mobiles/(?P<mobile>1[345789]\d{9})/count/$', views.MobileCountView.as_view()),
    re_path(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),
    re_path(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view()),
    re_path(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view()),
]
