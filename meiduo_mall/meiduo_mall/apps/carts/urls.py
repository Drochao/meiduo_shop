from django.urls import path

from carts import views

app_name = 'carts'

urlpatterns = [
    path('carts/', views.CartsView.as_view(), name="cart"),
    path('carts/selection/', views.CartsSelectAllView.as_view()),
    path('carts/simple/', views.CartSimpleView.as_view()),
]