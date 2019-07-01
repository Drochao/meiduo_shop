from django.urls import path

from wallet import views

app_name = 'wallet'

urlpatterns = [
    path('wallet/', views.WalletView.as_view(), name="wallet"),
]
