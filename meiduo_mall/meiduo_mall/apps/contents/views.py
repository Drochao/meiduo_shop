from django.shortcuts import render

from django.views import View

from contents.models import ContentCategory
from contents.utils import get_categories


class IndexView(View):
    """主页"""

    def get(self, request):
        """渲染主页"""

        categories = get_categories()

        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        context = {
            'categories': categories,
            'contents': contents
        }


        return render(request, 'index.html', context)

