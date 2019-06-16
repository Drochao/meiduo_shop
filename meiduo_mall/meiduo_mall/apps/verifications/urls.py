from django.urls import path, re_path

from verifications import views

app_name = 'verifications'
# /sms_codes/(?P<mobile>1[3-9]\d{9})/
urlpatterns = [
    re_path(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),
    re_path(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
    path('emails/verification/', views.VerifyEmailView.as_view())
]
