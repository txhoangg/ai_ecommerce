from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Staff, InventoryLog
from .serializers import StaffSerializer, StaffLoginSerializer, InventoryLogSerializer


class StaffListCreate(APIView):
    """
    GET: List all staff
    POST: Create new staff
    """
    
    def get(self, request):
        staff = Staff.objects.all()
        serializer = StaffSerializer(staff, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = StaffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffDetail(APIView):
    """
    GET: Retrieve staff details
    PUT: Update staff
    DELETE: Delete staff
    """
    
    def get_object(self, pk):
        try:
            return Staff.objects.get(pk=pk)
        except Staff.DoesNotExist:
            return None
    
    def get(self, request, pk):
        staff = self.get_object(pk)
        if staff is None:
            return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StaffSerializer(staff)
        return Response(serializer.data)
    
    def put(self, request, pk):
        staff = self.get_object(pk)
        if staff is None:
            return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = StaffSerializer(staff, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        staff = self.get_object(pk)
        if staff is None:
            return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)
        
        staff.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StaffLogin(APIView):
    """
    POST: Staff login
    """
    
    def post(self, request):
        serializer = StaffLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            try:
                staff = Staff.objects.get(email=email)
                if staff.check_password(password):
                    staff_data = StaffSerializer(staff).data
                    return Response({
                        'success': True,
                        'staff': staff_data
                    })
                else:
                    return Response({
                        'success': False,
                        'error': 'Invalid password'
                    }, status=status.HTTP_401_UNAUTHORIZED)
            except Staff.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Staff not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InventoryLogListCreate(APIView):
    """
    GET: List inventory logs
    POST: Create inventory log
    """
    
    def get(self, request):
        logs = InventoryLog.objects.all()
        serializer = InventoryLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = InventoryLogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
