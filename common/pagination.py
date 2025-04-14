"""
分页模块
提供自定义分页类，用于API响应中的标准分页处理
"""
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from .response import APIResponse


class StandardPagination(PageNumberPagination):
    """
    标准分页类
    基于页码的分页，提供标准API响应格式
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        重写响应方法，返回标准格式
        """
        return APIResponse(
            data=data,
            meta={
                'pagination': {
                    'page': self.page.number,
                    'page_size': self.get_page_size(self.request),
                    'total': self.page.paginator.count,
                    'total_pages': self.page.paginator.num_pages,
                    'links': {
                        'next': self.get_next_link(),
                        'previous': self.get_previous_link(),
                    }
                }
            }
        )


class StandardLimitOffsetPagination(LimitOffsetPagination):
    """
    基于偏移量的分页类
    提供标准API响应格式
    """
    default_limit = 10
    max_limit = 100
    
    def get_paginated_response(self, data):
        """
        重写响应方法，返回标准格式
        """
        return APIResponse(
            data=data,
            meta={
                'pagination': {
                    'limit': self.limit,
                    'offset': self.offset,
                    'total': self.count,
                    'links': {
                        'next': self.get_next_link(),
                        'previous': self.get_previous_link(),
                    }
                }
            }
        )
