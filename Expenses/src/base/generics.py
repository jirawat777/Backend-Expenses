from rest_framework import generics
from src.base.response import Response
from src.base.messages import messages


class ListAPIView(generics.ListAPIView):
    """
    List a queryset.
    """
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data,message=messages.GET_SUCCESS)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class RetrieveAPIView(generics.RetrieveAPIView):
    """
    Retrieve a model instance.
    """
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data,message=messages.GET_SUCCESS)