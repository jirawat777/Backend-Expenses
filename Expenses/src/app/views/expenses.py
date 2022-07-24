from django.shortcuts import render
from src.app.models.expenses import Expenses
from src.base.response import Response
from src.app.serializers.expenses import ExpensesSerializer
from src.base.generics import generics
from rest_framework import filters, generics, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

# Create your views here.


class ExpenseList(generics.ListAPIView):
    queryset = Expenses.objects.all()
    serializer_class = ExpensesSerializer
    filter_backend = [filters.SearchFilter,
                      filters.OrderingFilter, DjangoFilterBackend]
    filterset_fields = ['customer_id']
    orderring_fields = ['new_datetime']


class ExpenseCreate(APIView):
    queryset = Expenses.objects.all()
    serializer_class = ExpensesSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = ExpensesSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.data['name']
            update_by = serializer.data['update_by']
            price = serializer.data['price']
            description = serializer.data['description']
            destination = serializer.data['destination']
            image = serializer.data['image']

            items = Expenses(
                name=name,
                create_by=request.user.username,
                price=price,
                description=description,
                destination=destination,
            )
            items.save()
            return Response(request.data)
        else:
            return Response({'code': 'HTTP_400_BAD_REQUEST'}, status=status.HTTP_400_BAD_REQUEST, message='Cannot Create')
