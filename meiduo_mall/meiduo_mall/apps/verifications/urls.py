from django.urls import path, re_path

from verifications import views

app_name = 'verifications'
# /sms_codes/(?P<mobile>1[3-9]\d{9})/
urlpatterns = [
    re_path(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),
    re_path(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
    path('emails/verification/', views.VerifyEmailView.as_view()),
    re_path(r'^accounts/(?P<username>[a-zA-Z0-9_-]{5,20})/sms/token/$', views.VerifyUserView.as_view()),
    re_path(r'^sms_codes/$', views.SMSVerifyView.as_view()),
    re_path(r'^accounts/(?P<username>[a-zA-Z0-9_-]{5,20})/password/token/$', views.VerifyPasswordView.as_view()),
    re_path(r'^users/(?P<user_id>[\d]+)/password/$', views.ResetPassword.as_view()),
]
