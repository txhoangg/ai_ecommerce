from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Address
from .serializers import CustomerSerializer, AddressSerializer, CustomerLoginSerializer
import requests
from django.conf import settings


class CustomerListCreate(APIView):
    """
    GET: List all customers
    POST: Create new customer (automatically creates cart)
    """
    
    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            
            # Inter-service communication: Create cart for new customer
            try:
                cart_response = requests.post(
                    f"{settings.CART_SERVICE_URL}/api/carts/",
                    json={"customer_id": customer.id},
                    timeout=5
                )

                if cart_response.status_code in (200, 201):
                    # 201 = new cart created, 200 = existing cart returned
                    cart_data = cart_response.json()
                    response_data = serializer.data
                    response_data['cart_id'] = cart_data.get('id')
                    return Response(response_data, status=status.HTTP_201_CREATED)
                else:
                    # Cart creation failed, but customer created
                    return Response({
                        **serializer.data,
                        'warning': 'Customer created but cart creation failed'
                    }, status=status.HTTP_201_CREATED)
                    
            except requests.exceptions.RequestException as e:
                # Cart service unavailable
                return Response({
                    **serializer.data,
                    'warning': f'Customer created but cart service unavailable: {str(e)}'
                }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerDetail(APIView):
    """
    GET: Retrieve customer details
    PUT: Update customer
    DELETE: Delete customer
    """
    
    def get_object(self, pk):
        try:
            return Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            return None
    
    def get(self, request, pk):
        customer = self.get_object(pk)
        if customer is None:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)
    
    def put(self, request, pk):
        customer = self.get_object(pk)
        if customer is None:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        customer = self.get_object(pk)
        if customer is None:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        customer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerLogin(APIView):
    """
    POST: Customer login
    """
    
    def post(self, request):
        serializer = CustomerLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            try:
                customer = Customer.objects.get(email=email)
                if customer.check_password(password):
                    customer_data = CustomerSerializer(customer).data
                    return Response({
                        'success': True,
                        'customer': customer_data
                    })
                else:
                    return Response({
                        'success': False,
                        'error': 'Invalid password'
                    }, status=status.HTTP_401_UNAUTHORIZED)
            except Customer.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Customer not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressListCreate(APIView):
    """
    GET: List customer addresses
    POST: Add new address
    """
    
    def get(self, request, customer_id):
        addresses = Address.objects.filter(customer_id=customer_id)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)
    
    def post(self, request, customer_id):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=customer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
