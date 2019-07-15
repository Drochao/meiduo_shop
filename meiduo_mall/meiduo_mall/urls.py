"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include

urlpatterns = [
    path('', include('users.urls', namespace='users')),
    path('', include('contents.urls', namespace='contents')),
    path('', include('verifications.urls', namespace='verifications')),
    path('', include('oauth.urls', namespace='oauth')),
    path('', include('areas.urls', namespace='areas')),
    path('', include('goods.urls', namespace='goods')),
    path('', include('carts.urls', namespace='carts')),
    path('', include('payment.urls', namespace='payment')),
    path('', include('wallet.urls', namespace='wallet')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('search/', include('haystack.urls')),
    path('', include('coupons.urls', namespace="coupons")),
    path('meiduo_admin/', include('meiduo_admin.urls', namespace='meiduo_admin'))
]
