from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Manager, Report, ManagerActivity
from .serializers import (
    ManagerSerializer, ManagerLoginSerializer, ReportSerializer,
    ManagerActivitySerializer, SalesReportRequestSerializer
)
import requests
from django.conf import settings
from datetime import datetime
from decimal import Decimal


class ManagerListCreate(APIView):
    """
    GET: List all managers
    POST: Create new manager
    """
    
    def get(self, request):
        managers = Manager.objects.all()
        serializer = ManagerSerializer(managers, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ManagerSerializer(data=request.data)
        if serializer.is_valid():
            password = request.data.get('password')
            manager = serializer.save()
            if password:
                manager.set_password(password)
                manager.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManagerDetail(APIView):
    """
    GET: Retrieve manager details
    PUT: Update manager
    DELETE: Delete manager
    """
    
    def get_object(self, pk):
        try:
            return Manager.objects.get(pk=pk)
        except Manager.DoesNotExist:
            return None
    
    def get(self, request, pk):
        manager = self.get_object(pk)
        if manager is None:
            return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ManagerSerializer(manager)
        return Response(serializer.data)
    
    def put(self, request, pk):
        manager = self.get_object(pk)
        if manager is None:
            return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ManagerSerializer(manager, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Log activity
            ManagerActivity.objects.create(
                manager_id=pk,
                action='Updated profile',
                description='Manager updated their profile information'
            )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        manager = self.get_object(pk)
        if manager is None:
            return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
        
        manager.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ManagerLogin(APIView):
    """
    POST: Manager login
    """
    
    def post(self, request):
        serializer = ManagerLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            try:
                manager = Manager.objects.get(email=email)
                if manager.check_password(password):
                    # Log activity
                    ManagerActivity.objects.create(
                        manager_id=manager.id,
                        action='Login',
                        description='Manager logged in'
                    )
                    
                    manager_data = ManagerSerializer(manager).data
                    return Response({
                        'success': True,
                        'manager': manager_data
                    })
                else:
                    return Response({
                        'success': False,
                        'error': 'Invalid password'
                    }, status=status.HTTP_401_UNAUTHORIZED)
            except Manager.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Manager not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportListCreate(APIView):
    """
    GET: List all reports
    POST: Create new report
    """
    
    def get(self, request):
        reports = Report.objects.all()
        
        # Filter by manager
        manager_id = request.query_params.get('manager_id')
        if manager_id:
            reports = reports.filter(manager_id=manager_id)
        
        # Filter by type
        report_type = request.query_params.get('type')
        if report_type:
            reports = reports.filter(report_type=report_type)
        
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ReportSerializer(data=request.data)
        if serializer.is_valid():
            report = serializer.save()
            
            # Log activity
            ManagerActivity.objects.create(
                manager_id=report.manager_id,
                action='Created report',
                description=f'Created {report.report_type} report: {report.title}'
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportDetail(APIView):
    """
    GET: Retrieve report details
    DELETE: Delete report
    """
    
    def get(self, request, pk):
        try:
            report = Report.objects.get(pk=pk)
        except Report.DoesNotExist:
            return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ReportSerializer(report)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        try:
            report = Report.objects.get(pk=pk)
        except Report.DoesNotExist:
            return Response({'error': 'Report not found'}, status=status.HTTP_404_NOT_FOUND)
        
        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SalesReport(APIView):
    """
    POST: Generate sales report
    """
    
    def post(self, request):
        serializer = SalesReportRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        
        # Get orders from order-service
        try:
            orders_response = requests.get(
                f"{settings.ORDER_SERVICE_URL}/api/orders/",
                timeout=5
            )
            
            if orders_response.status_code != 200:
                return Response({'error': 'Failed to fetch orders'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            orders = orders_response.json()
            
            # Filter by date range
            filtered_orders = []
            for order in orders:
                order_date = datetime.fromisoformat(order['created_at'].replace('Z', '+00:00')).date()
                if start_date <= order_date <= end_date:
                    filtered_orders.append(order)
            
            # Calculate statistics
            total_orders = len(filtered_orders)
            total_revenue = sum(Decimal(str(order['final_amount'])) for order in filtered_orders)
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            
            # Count by status
            status_counts = {}
            for order in filtered_orders:
                order_status = order['status']
                status_counts[order_status] = status_counts.get(order_status, 0) + 1
            
            report_content = f"""
Sales Report
Period: {start_date} to {end_date}

Summary:
- Total Orders: {total_orders}
- Total Revenue: ${total_revenue:.2f}
- Average Order Value: ${avg_order_value:.2f}

Orders by Status:
{chr(10).join(f'- {status}: {count}' for status, count in status_counts.items())}
            """
            
            return Response({
                'report_type': 'sales',
                'start_date': start_date,
                'end_date': end_date,
                'total_orders': total_orders,
                'total_revenue': float(total_revenue),
                'avg_order_value': float(avg_order_value),
                'status_counts': status_counts,
                'content': report_content.strip()
            })
            
        except requests.exceptions.RequestException as e:
            return Response({'error': f'Order service unavailable: {str(e)}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class InventoryReport(APIView):
    """
    GET: Generate inventory report
    """
    
    def get(self, request):
        # Get books from book-service
        try:
            books_response = requests.get(
                f"{settings.BOOK_SERVICE_URL}/api/books/",
                timeout=5
            )
            
            if books_response.status_code != 200:
                return Response({'error': 'Failed to fetch books'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            books = books_response.json()
            
            # Calculate statistics
            total_books = len(books)
            total_stock = sum(book.get('stock', 0) for book in books)
            low_stock_books = [book for book in books if book.get('stock', 0) < 10]
            out_of_stock_books = [book for book in books if book.get('stock', 0) == 0]
            
            report_content = f"""
Inventory Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
- Total Books: {total_books}
- Total Stock: {total_stock}
- Low Stock Items: {len(low_stock_books)}
- Out of Stock Items: {len(out_of_stock_books)}

Low Stock Books (< 10):
{chr(10).join(f'- {book["title"]}: {book.get("stock", 0)} units' for book in low_stock_books[:10])}
            """
            
            return Response({
                'report_type': 'inventory',
                'total_books': total_books,
                'total_stock': total_stock,
                'low_stock_count': len(low_stock_books),
                'out_of_stock_count': len(out_of_stock_books),
                'low_stock_books': low_stock_books[:10],
                'content': report_content.strip()
            })
            
        except requests.exceptions.RequestException as e:
            return Response({'error': f'Book service unavailable: {str(e)}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class CustomerReport(APIView):
    """
    GET: Generate customer report
    """
    
    def get(self, request):
        # Get customers from customer-service
        try:
            customers_response = requests.get(
                f"{settings.CUSTOMER_SERVICE_URL}/api/customers/",
                timeout=5
            )
            
            if customers_response.status_code != 200:
                return Response({'error': 'Failed to fetch customers'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            customers = customers_response.json()

            # Calculate statistics
            total_customers = len(customers)
            # Customer model does not have is_active; count all as active
            active_customers = total_customers

            report_content = f"""
Customer Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
- Total Customers: {total_customers}
- Active Customers: {active_customers}
            """

            return Response({
                'report_type': 'customer',
                'total_customers': total_customers,
                'active_customers': active_customers,
                'inactive_customers': 0,
                'content': report_content.strip()
            })
            
        except requests.exceptions.RequestException as e:
            return Response({'error': f'Customer service unavailable: {str(e)}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class StaffReport(APIView):
    """
    GET: Generate staff performance report
    """
    
    def get(self, request):
        # Get staff from staff-service
        try:
            staff_response = requests.get(
                f"{settings.STAFF_SERVICE_URL}/api/staff/",
                timeout=5
            )
            
            if staff_response.status_code != 200:
                return Response({'error': 'Failed to fetch staff'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            staff_list = staff_response.json()

            # Calculate statistics
            total_staff = len(staff_list)
            # Staff model does not have is_active; count all as active
            active_staff = total_staff

            report_content = f"""
Staff Performance Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
- Total Staff: {total_staff}
- Active Staff: {active_staff}
            """

            return Response({
                'report_type': 'staff',
                'total_staff': total_staff,
                'active_staff': active_staff,
                'inactive_staff': 0,
                'content': report_content.strip()
            })
            
        except requests.exceptions.RequestException as e:
            return Response({'error': f'Staff service unavailable: {str(e)}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class ManagerActivityList(APIView):
    """
    GET: List manager activities
    """
    
    def get(self, request, manager_id):
        activities = ManagerActivity.objects.filter(manager_id=manager_id)
        serializer = ManagerActivitySerializer(activities, many=True)
        return Response(serializer.data)
