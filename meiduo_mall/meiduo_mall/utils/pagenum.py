from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PageNum(PageNumberPagination):

    page_size = 5  # 默认每页数量
    page_size_query_param = 'page_size'
    max_page_size = 4

    # 重写分页返回方法，按照指定的字段进行分页数据返回
    def get_paginated_response(self, data):

        return Response({
            'count': self.page.paginator.count,  # 总数量
            'lists': data,  # 用户数据
            'page': self.page.number,  # 当前页数
            'pages': self.page.paginator.num_pages,  # 总页数
            'pagesize': self.page_size  # 后端指定的页容量
        })
