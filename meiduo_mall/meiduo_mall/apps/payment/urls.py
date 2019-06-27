from django.urls import re_path, path

from payment import views

app_name = 'payment'

urlpatterns = [
    re_path(r'^payment/(?P<order_id>\d+)/$', views.PaymentView.as_view()),
    path('payment/status/', views.PaymentStatusView.as_view())
]
