from django.shortcuts import render

from django.views import View


class IndexView(View):
    """主页"""

    def get(self, request):
        """渲染主页"""
        return render(request, 'index.html')

    def post(self, request):
        pass
