from django.urls import path

from areas import views

app_name = 'areas'

urlpatterns = [
    path('areas/', views.AreasView.as_view(), name="areas"),
]
