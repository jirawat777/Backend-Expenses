from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import APIException
from rest_framework import status
from src.base.response import Response

class NotFound(APIException):
    status_code = status.HTTP_200_OK
    default_detail = ('bad_request.')
    default_code = 'bad_request'

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50000

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })

class PropertyListPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'

    def paginate_queryset(self, queryset, request, view=None):
        page_size = self.get_page_size(request)
        if not page_size:
            return Response({
                'size': page_size,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'count': self.page.paginator.count,
                'results': data
            })

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pagesprint('text', varaible, file=sys.stderr)
        try:
            self.page = paginator.page(page_number)
        except Exception as exc:
            msg = {
                "code": 400,
                "error": "Page out of range"
            }
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            self.display_page_controls = True
        self.request = request
        return list(self.page)

class MonitorListPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'

    def paginate_queryset(self, queryset, request, view=None):
        page_size = self.get_page_size(request)
        if not page_size:
            return Response({
                'size': page_size,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'count': self.page.paginator.count,
                'results': data
            })

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pagesprint('text', varaible, file=sys.stderr)
        try:
            self.page = paginator.page(page_number)
        except Exception as exc:
            msg = {
                "code": 400,
                "error": "Page out of range"
            }
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            self.display_page_controls = True
        self.request = request
        return list(self.page)

class SearchMassagePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 1000
    def get_paginated_response(self,data):
        if len(data) == 0:
            return Response({
                "msg" : "Data Not Found",
                "results" : data,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'count': self.page.paginator.count,
            })
        else:
            return Response({
                "msg": "Success OK 200!",
                "results" : data,
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'count': self.page.paginator.count,
            })
