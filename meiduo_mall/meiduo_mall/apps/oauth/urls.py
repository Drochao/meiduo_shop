
from django.urls import path

from oauth import views

app_name = 'oauth'
urlpatterns = [
    path('qq/authorization/', views.QQAuthURLView.as_view()),
    path('oauth_callback/', views.QQAuthView.as_view())
]
