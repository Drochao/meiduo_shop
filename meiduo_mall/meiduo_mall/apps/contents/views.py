
from django.shortcuts import render


# Create your views here.
from django.urls import reverse
from django.views import View


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')

    def post(self, request):
        pass