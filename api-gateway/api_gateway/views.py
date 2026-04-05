from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import requests
import jwt
import datetime
from django.conf import settings
from django.http import JsonResponse
import json

SHARED_SECRET = "super-secret-jwt-key"

def generate_jwt(user_id, role):
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, SHARED_SECRET, algorithm='HS256')

# Helper function to make API calls
def api_call(request, method, url, data=None, timeout=5):
    headers = {}
    if hasattr(request, 'session') and 'jwt_token' in request.session:
        headers['Authorization'] = f"Bearer {request.session['jwt_token']}"
        
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=timeout)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers, timeout=timeout)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            return None

        if response.status_code == 204:
            # No Content — DELETE successful
            return True
        if response.status_code in [200, 201]:
            try:
                return response.json()
            except Exception:
                return True
        return None
    except requests.exceptions.RequestException:
        return None


# Helper to get session context for all user types
def get_session_context(request):
    return {
        'customer': request.session.get('customer'),
        'staff': request.session.get('staff'),
        'manager': request.session.get('manager'),
    }


# Home page
def home(request):
    # Get popular books from recommender service
    popular_books = api_call(request, 'GET', f"{settings.RECOMMENDER_SERVICE_URL}/api/recommendations/popular/?limit=8")
    
    # Get all books if popular books not available
    if not popular_books:
        popular_books = api_call(request, 'GET', f"{settings.BOOK_SERVICE_URL}/api/books/")
        if popular_books:
            popular_books = popular_books[:8]
    
    context = get_session_context(request)
    context['popular_books'] = popular_books or []
    return render(request, 'home.html', context)


# Unified login - auto-detect user type
def login(request):
    if request.method == 'POST':
        data = {
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
        }

        # Try customer login first
        result = api_call(request, 'POST', f"{settings.CUSTOMER_SERVICE_URL}/api/customers/login/", data)
        if result and result.get('success'):
            request.session['jwt_token'] = generate_jwt(result['customer']['id'], 'customer')
            request.session['customer'] = result['customer']
            messages.success(request, f"Welcome back, {result['customer']['name']}!")
            return redirect('home')

        # Try staff login
        result = api_call(request, 'POST', f"{settings.STAFF_SERVICE_URL}/api/staff/login/", data)
        if result and result.get('success'):
            request.session['jwt_token'] = generate_jwt(result['staff']['id'], 'staff')
            request.session['staff'] = result['staff']
            messages.success(request, f"Welcome, {result['staff']['name']}!")
            return redirect('staff_dashboard')

        # Try manager login
        result = api_call(request, 'POST', f"{settings.MANAGER_SERVICE_URL}/api/managers/login/", data)
        if result and result.get('success'):
            request.session['jwt_token'] = generate_jwt(result['manager']['id'], 'manager')
            request.session['manager'] = result['manager']
            messages.success(request, f"Welcome, {result['manager']['name']}!")
            return redirect('manager_dashboard')

        messages.error(request, 'Invalid email or password.')

    return render(request, 'login.html')


# Unified logout
def logout(request):
    request.session.pop('customer', None)
    request.session.pop('staff', None)
    request.session.pop('manager', None)
    request.session.pop('jwt_token', None)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


# Customer registration
def customer_register(request):
    if request.method == 'POST':
        data = {
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
        }
        
        result = api_call(request, 'POST', f"{settings.CUSTOMER_SERVICE_URL}/api/customers/", data)
        
        if result:
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        else:
            messages.error(request, 'Registration failed. Email may already exist.')
    
    return render(request, 'customer/register.html')


# Customer login
def customer_login(request):
    if request.method == 'POST':
        data = {
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
        }
        
        result = api_call(request, 'POST', f"{settings.CUSTOMER_SERVICE_URL}/api/customers/login/", data)
        
        if result and result.get('success'):
            request.session['jwt_token'] = generate_jwt(result['customer']['id'], 'customer')
            request.session['customer'] = result['customer']
            messages.success(request, f"Welcome back, {result['customer']['name']}!")
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'customer/login.html')


# Customer logout
def customer_logout(request):
    request.session.pop('customer', None)
    request.session.pop('jwt_token', None)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


# Customer profile
def customer_profile(request):
    if 'customer' not in request.session:
        messages.error(request, 'Please login first.')
        return redirect('login')
    
    customer = request.session['customer']
    
    # Get customer orders
    orders = api_call(request, 'GET', f"{settings.ORDER_SERVICE_URL}/api/orders/?customer_id={customer['id']}")
    
    context = get_session_context(request)
    context['orders'] = orders or []
    return render(request, 'customer/profile.html', context)


# Staff login
def staff_login(request):
    if request.method == 'POST':
        data = {
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
        }
        
        result = api_call(request, 'POST', f"{settings.STAFF_SERVICE_URL}/api/staff/login/", data)
        
        if result and result.get('success'):
            request.session['jwt_token'] = generate_jwt(result['staff']['id'], 'staff')
            request.session['staff'] = result['staff']
            messages.success(request, f"Welcome, {result['staff']['name']}!")
            return redirect('staff_dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'staff/login.html')


# Staff logout
def staff_logout(request):
    request.session.pop('staff', None)
    request.session.pop('jwt_token', None)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


# Staff dashboard
def staff_dashboard(request):
    if 'staff' not in request.session:
        messages.error(request, 'Please login first.')
        return redirect('login')
    
    staff = request.session['staff']
    
    # Get statistics
    books = api_call(request, 'GET', f"{settings.BOOK_SERVICE_URL}/api/books/")
    orders = api_call(request, 'GET', f"{settings.ORDER_SERVICE_URL}/api/orders/")
    
    context = get_session_context(request)
    context.update({
        'total_books': len(books) if books else 0,
        'total_orders': len(orders) if orders else 0,
        'low_stock_books': [b for b in (books or []) if b.get('stock', 0) < 10],
    })
    return render(request, 'staff/dashboard.html', context)


# Staff books management
def staff_books(request):
    if 'staff' not in request.session:
        messages.error(request, 'Please login first.')
        return redirect('login')
    
    books = api_call(request, 'GET', f"{settings.BOOK_SERVICE_URL}/api/books/")
    categories = api_call(request, 'GET', f"{settings.CATALOG_SERVICE_URL}/api/categories/")
    
    context = get_session_context(request)
    context.update({'books': books or [], 'categories': categories or []})
    return render(request, 'staff/books.html', context)


# Staff add book
def staff_add_book(request):
    if 'staff' not in request.session:
        messages.error(request, 'Please login first.')
        return redirect('login')
    
    if request.method == 'POST':
        data = {
            'title': request.POST.get('title'),
            'author': request.POST.get('author'),
            'price': float(request.POST.get('price')),
            'stock': int(request.POST.get('stock')),
            'description': request.POST.get('description', ''),
            'category_id': int(request.POST.get('category_id')) if request.POST.get('category_id') else None,
            'staff_id': request.session['staff']['id'],
        }
        
        result = api_call(request, 'POST', f"{settings.BOOK_SERVICE_URL}/api/books/", data)
        
        if result:
            messages.success(request, 'Book added successfully!')
            return redirect('staff_books')
        else:
            messages.error(request, 'Failed to add book.')
    
    categories = api_call(request, 'GET', f"{settings.CATALOG_SERVICE_URL}/api/categories/")
    
    context = get_session_context(request)
    context['categories'] = categories or []
    return render(request, 'staff/add_book.html', context)


# Staff edit book
def staff_edit_book(request, book_id):
    if 'staff' not in request.session:
        messages.error(request, 'Please login first.')
        return redirect('login')
    
    book = api_call(request, 'GET', f"{settings.BOOK_SERVICE_URL}/api/books/{book_id}/")
    
    if not book:
        messages.error(request, 'Book not found.')
        return redirect('staff_books')
    
    if request.method == 'POST':
        data = {
            'title': request.POST.get('title'),
            'author': request.POST.get('author'),
            'price': float(request.POST.get('price')),
            'stock': int(request.POST.get('stock')),
            'description': request.POST.get('description', ''),
            'category_id': int(request.POST.get('category_id')) if request.POST.get('category_id') else None,
        }
        
        result = api_call(request, 'PUT', f"{settings.BOOK_SERVICE_URL}/api/books/{book_id}/", data)
        
        if result:
            messages.success(request, 'Book updated successfully!')
            return redirect('staff_books')
        else:
            messages.error(request, 'Failed to update book.')
    
    categories = api_call(request, 'GET', f"{settings.CATALOG_SERVICE_URL}/api/categories/")
    
    context = get_session_context(request)
    context.update({'book': book, 'categories': categories or []})
    return render(request, 'staff/edit_book.html', context)


# Staff delete book
def staff_delete_book(request, book_id):
    if 'staff' not in request.session:
        messages.error(request, 'Please login first.')
        return redirect('login')

    if request.method == 'POST':
        result = api_call(request, 'DELETE', f"{settings.BOOK_SERVICE_URL}/api/books/{book_id}/")

        if result:
            messages.success(request, 'Book deleted successfully!')
        else:
            messages.error(request, 'Failed to delete book.')

    return redirect('staff_books')


# Staff orders management
def staff_orders(request):
    if 'staff' not in request.session:
        messages.error(request, 'Please login first.')
        return redirect('login')
    
    orders = api_call(request, 'GET', f"{settings.ORDER_SERVICE_URL}/api/orders/")
    
    context = get_session_context(request)
    if isinstance(orders, list):
        orders.sort(key=lambda x: str(x.get('created_at', '')), reverse=True)
        
    context['orders'] = orders or []
    return render(request, 'staff/orders.html', context)


# Staff update order status
def staff_update_order_status(request, order_id):
    if 'staff' not in request.session:
        messages.error(request, 'Please login first.')
        return redirect('login')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        data = {'status': new_status}
        
        result = api_call(request, 'PUT', f"{settings.ORDER_SERVICE_URL}/api/orders/{order_id}/", data)
        
        if result:
            messages.success(request, f'Order #{order_id} status updated to {new_status}.')
        else:
            messages.error(request, 'Failed to update order status.')
            
    return redirect('staff_orders')


# Manager login
def manager_login(request):
    if request.method == 'POST':
        data = {
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
        }
        
        result = api_call(request, 'POST', f"{settings.MANAGER_SERVICE_URL}/api/managers/login/", data)
        
        if result and result.get('success'):
            request.session['jwt_token'] = generate_jwt(result['manager']['id'], 'manager')
            request.session['manager'] = result['manager']
            messages.success(request, f"Welcome, {result['manager']['name']}!")
            return redirect('manager_dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'manager/login.html')


# Manager logout
def manager_logout(request):
    request.session.pop('manager', None)
    request.session.pop('jwt_token', None)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')


# Manager dashboard
def manager_dashboard(request):
    if 'manager' not in request.session:
        messages.error(request, 'Please login first.')
        return redirect('login')
    
    manager = request.session['manager']
    
    # Get reports
    from datetime import date
    today = date.today()
    sales_report = api_call(request, 'POST', f"{settings.MANAGER_SERVICE_URL}/api/reports/sales/", {
        'start_date': str(today.replace(day=1)),
        'end_date': str(today),
    })
    inventory_report = api_call(request, 'GET', f"{settings.MANAGER_SERVICE_URL}/api/reports/inventory/")
    customer_report = api_call(request, 'GET', f"{settings.MANAGER_SERVICE_URL}/api/reports/customers/")
    
    context = get_session_context(request)
    context.update({
        'sales_report': sales_report,
        'inventory_report': inventory_report,
        'customer_report': customer_report,
    })
    return render(request, 'manager/dashboard.html', context)


# Manager reports
def manager_reports(request):
    if 'manager' not in request.session:
        messages.error(request, 'Please login first.')
        return redirect('login')
    
    reports = api_call(request, 'GET', f"{settings.MANAGER_SERVICE_URL}/api/reports/?manager_id={request.session['manager']['id']}")
    
    context = get_session_context(request)
    context['reports'] = reports or []
    return render(request, 'manager/reports.html', context)


# Book list
def book_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    page_number = request.GET.get('page', 1)
    
    books = api_call(request, 'GET', f"{settings.BOOK_SERVICE_URL}/api/books/")
    categories = api_call(request, 'GET', f"{settings.CATALOG_SERVICE_URL}/api/categories/")
    
    # Filter books
    if books:
        if query:
            books = [b for b in books if query.lower() in b.get('title', '').lower() or query.lower() in b.get('author', '').lower()]
        if category_id:
            books = [b for b in books if b.get('category_id') == int(category_id)]
    
    paginator = Paginator(books or [], 12)
    page_obj = paginator.get_page(page_number)
    
    context = get_session_context(request)
    context.update({
        'books': page_obj,
        'categories': categories or [],
        'query': query,
        'selected_category': category_id,
    })
    return render(request, 'books/list.html', context)


# Book detail
def book_detail(request, book_id):
    book = api_call(request, 'GET', f"{settings.BOOK_SERVICE_URL}/api/books/{book_id}/")
    
    if not book:
        messages.error(request, 'Book not found.')
        return redirect('book_list')
    
    # Get ratings and reviews
    ratings = api_call(request, 'GET', f"{settings.COMMENT_RATE_SERVICE_URL}/api/ratings/book/{book_id}/")
    reviews = api_call(request, 'GET', f"{settings.COMMENT_RATE_SERVICE_URL}/api/reviews/book/{book_id}/")

    # Calculate average rating
    if isinstance(ratings, dict):
        ratings_list = ratings.get('ratings', [])
        avg_rating = ratings.get('average')
    else:
        ratings_list = ratings or []
        avg_rating = (sum(r['score'] for r in ratings_list) / len(ratings_list)) if ratings_list else None

    context = get_session_context(request)
    reviews_response = reviews
    if isinstance(reviews_response, dict):
        reviews_list = reviews_response.get('reviews', [])
    else:
        reviews_list = reviews_response or []

    for review in reviews_list:
        customer_info = api_call(request, 'GET', f"{settings.CUSTOMER_SERVICE_URL}/api/customers/{review.get('customer_id')}/")
        if customer_info and 'name' in customer_info:
            review['customer_name'] = customer_info['name']
        else:
            review['customer_name'] = f"Customer {review.get('customer_id')}"
            
        # Match rating score to this review based on customer_id
        for r in ratings_list:
            if r.get('customer_id') == review.get('customer_id'):
                review['score'] = r.get('score')
                break

    context.update({
        'book': book,
        'ratings': ratings_list,
        'reviews': reviews_list,
        'avg_rating': avg_rating,
    })
    return render(request, 'books/detail.html', context)


# Rate and Review book
def rate_and_review_book(request, book_id):
    if 'customer' not in request.session:
        messages.error(request, 'Please login to interact with books.')
        return redirect('login')
    
    if request.method == 'POST':
        customer_id = request.session['customer']['id']
        score_str = request.POST.get('score')
        comment = request.POST.get('comment')
        
        success = []
        fails = []
        
        if score_str:
            data = {
                'customer_id': customer_id,
                'book_id': book_id,
                'score': float(score_str)
            }
            if api_call(request, 'POST', f"{settings.COMMENT_RATE_SERVICE_URL}/api/ratings/", data):
                success.append("rating")
            else:
                fails.append("rating")
                
        if comment and comment.strip():
            data = {
                'customer_id': customer_id,
                'book_id': book_id,
                'comment': comment.strip()
            }
            if api_call(request, 'POST', f"{settings.COMMENT_RATE_SERVICE_URL}/api/reviews/", data):
                success.append("review")
            else:
                fails.append("review")
                
        if not score_str and not (comment and comment.strip()):
            messages.warning(request, 'Please provide a rating or a review.')
        else:
            if success:
                messages.success(request, f'Successfully submitted your {" and ".join(success)}!')
            if fails:
                messages.error(request, f'Failed to submit {" and ".join(fails)}.')
                
    return redirect('book_detail', book_id=book_id)


# Book recommendations
def book_recommendations(request):
    if 'customer' not in request.session:
        # Show popular books for non-logged-in users
        recommendations = api_call(request, 'GET', f"{settings.RECOMMENDER_SERVICE_URL}/api/recommendations/popular/?limit=12")
        rec_source = 'popular'
    else:
        customer_id = request.session['customer']['id']

        # Try NCF deep learning model first
        ncf_data = api_call(request, 'GET', f"{settings.RECOMMENDER_SERVICE_URL}/api/ai/model/recommend/{customer_id}/?limit=12")
        if ncf_data and isinstance(ncf_data, dict) and ncf_data.get('recommendations'):
            # NCF model returned results — reformat to match template expectations
            recommendations = []
            for item in ncf_data['recommendations']:
                book = item.get('book', {})
                book['score'] = item.get('score', 0)
                book['reason'] = item.get('reason', 'Deep learning recommendation')
                recommendations.append(book)
            rec_source = 'ncf_model'
        else:
            # Fallback: use hybrid collaborative-content algorithm
            api_call(request, 'POST', f"{settings.RECOMMENDER_SERVICE_URL}/api/recommendations/generate/", {'customer_id': customer_id, 'limit': 12})
            rec_result = api_call(request, 'GET', f"{settings.RECOMMENDER_SERVICE_URL}/api/recommendations/{customer_id}/")
            recommendations = rec_result or []
            rec_source = 'hybrid'

    context = get_session_context(request)
    context['recommendations'] = recommendations or []
    context['rec_source'] = rec_source
    return render(request, 'books/recommendations.html', context)


# Cart view
def cart_view(request):
    if 'customer' not in request.session:
        messages.error(request, 'Please login to view cart.')
        return redirect('login')
    
    customer_id = request.session['customer']['id']
    cart = api_call(request, 'GET', f"{settings.CART_SERVICE_URL}/api/carts/{customer_id}/")

    # Enrich cart items with book titles
    if cart and cart.get('items'):
        for item in cart['items']:
            book = api_call(request, 'GET', f"{settings.BOOK_SERVICE_URL}/api/books/{item['book_id']}/")
            item['book_title'] = book['title'] if book else f"Book #{item['book_id']}"

    context = get_session_context(request)
    context['cart'] = cart or {'items': [], 'total': 0}
    return render(request, 'cart/view.html', context)


# Add to cart
def cart_add(request, book_id):
    if 'customer' not in request.session:
        messages.error(request, 'Please login to add items to cart.')
        return redirect('login')
    
    data = {
        'customer_id': request.session['customer']['id'],
        'book_id': book_id,
        'quantity': int(request.POST.get('quantity', 1)) if request.method == 'POST' else 1,
    }

    result = api_call(request, 'POST', f"{settings.CART_SERVICE_URL}/api/cart-items/", data)

    if result:
        book = api_call(request, 'GET', f"{settings.BOOK_SERVICE_URL}/api/books/{book_id}/")
        book_title = book.get('title') if book else f"Book #{book_id}"
        messages.success(request, f'"{book_title}" added to cart!')
    else:
        messages.error(request, 'Failed to add book to cart.')

    referer = request.META.get('HTTP_REFERER', '/books/')
    return redirect(referer)


# Update cart item
def cart_update(request, item_id):
    if 'customer' not in request.session:
        messages.error(request, 'Please login first.')
        return redirect('login')
    
    if request.method == 'POST':
        data = {
            'quantity': int(request.POST.get('quantity')),
            'customer_id': request.session['customer']['id'],
        }

        result = api_call(request, 'PUT', f"{settings.CART_SERVICE_URL}/api/cart-items/{item_id}/", data)
        
        if result:
            messages.success(request, 'Cart updated!')
        else:
            messages.error(request, 'Failed to update cart.')
    
    return redirect('cart_view')


# Remove from cart
def cart_remove(request, item_id):
    if 'customer' not in request.session:
        messages.error(request, 'Please login first.')
        return redirect('login')

    if request.method == 'POST':
        customer_id = request.session['customer']['id']
        result = api_call(request, 'DELETE', f"{settings.CART_SERVICE_URL}/api/cart-items/{item_id}/?customer_id={customer_id}")

        if result:
            messages.success(request, 'Item removed from cart!')
        else:
            messages.error(request, 'Failed to remove item.')

    return redirect('cart_view')


# Order list
def order_list(request):
    if 'customer' not in request.session:
        messages.error(request, 'Please login to view orders.')
        return redirect('login')
    
    customer_id = request.session['customer']['id']
    orders = api_call(request, 'GET', f"{settings.ORDER_SERVICE_URL}/api/orders/?customer_id={customer_id}")
    
    context = get_session_context(request)
    context['orders'] = orders or []
    return render(request, 'orders/list.html', context)


# Order detail
def order_detail(request, order_id):
    if 'customer' not in request.session:
        messages.error(request, 'Please login to view orders.')
        return redirect('login')
    
    order = api_call(request, 'GET', f"{settings.ORDER_SERVICE_URL}/api/orders/{order_id}/")

    if not order:
        messages.error(request, 'Order not found.')
        return redirect('order_list')

    # Ownership check: ensure this order belongs to the logged-in customer
    if str(order.get('customer_id')) != str(request.session['customer']['id']):
        messages.error(request, 'Access denied: this order does not belong to you.')
        return redirect('order_list')

    # Enrich order items with book titles
    if order and order.get('items'):
        for item in order['items']:
            book = api_call(request, 'GET', f"{settings.BOOK_SERVICE_URL}/api/books/{item['book_id']}/")
            item['book_title'] = book['title'] if book else f"Book #{item['book_id']}"
    
    context = get_session_context(request)
    context['order'] = order
    return render(request, 'orders/detail.html', context)


# Checkout
def checkout(request):
    if 'customer' not in request.session:
        messages.error(request, 'Please login to checkout.')
        return redirect('login')
    
    customer_id = request.session['customer']['id']
    
    if request.method == 'POST':
        data = {
            'customer_id': customer_id,
            'payment_method': request.POST.get('payment_method'),
            'shipping_method': request.POST.get('shipping_method'),
            'shipping_address': request.POST.get('shipping_address'),
            'discount_code': request.POST.get('discount_code', ''),
        }
        
        result = api_call(request, 'POST', f"{settings.ORDER_SERVICE_URL}/api/orders/create/", data)
        
        if result:
            messages.success(request, 'Order placed successfully!')
            return redirect('order_detail', order_id=result['order']['id'])
        else:
            messages.error(request, 'Failed to place order.')
    
    # Get cart
    cart = api_call(request, 'GET', f"{settings.CART_SERVICE_URL}/api/carts/{customer_id}/")

    # Enrich cart items with book titles
    if cart and cart.get('items'):
        for item in cart['items']:
            book = api_call(request, 'GET', f"{settings.BOOK_SERVICE_URL}/api/books/{item['book_id']}/")
            item['book_title'] = book['title'] if book else f"Book #{item['book_id']}"

    context = get_session_context(request)
    context['cart'] = cart or {'items': [], 'total': 0}
    return render(request, 'orders/checkout.html', context)

def chat_page(request):
    """AI Chat page"""
    customer = request.session.get('customer')
    context = get_session_context(request)
    return render(request, 'chat.html', context)


@csrf_exempt
def chat_api(request):
    """Proxy chat POST request to recommender-ai-service"""
    import json as _json
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        body = _json.loads(request.body)
    except Exception:
        body = {}

    customer = request.session.get('customer')
    if customer:
        body['customer_id'] = customer.get('id')

    session_id = request.session.get('chat_session_id')
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
        request.session['chat_session_id'] = session_id
    body['session_id'] = session_id

    try:
        resp = requests.post(
            f"{settings.RECOMMENDER_SERVICE_URL}/api/ai/chat/",
            json=body,
            timeout=30
        )
        return JsonResponse(resp.json(), status=resp.status_code)
    except Exception as e:
        return JsonResponse({'error': str(e), 'response': 'Xin lỗi, dịch vụ chat đang không khả dụng.'}, status=503)


# Validate discount
def validate_discount(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            result = api_call(request, 'POST', f"{settings.ORDER_SERVICE_URL}/api/discounts/validate/", data)
            if result:
                return JsonResponse(result)
        except Exception as e:
            pass
    return JsonResponse({'valid': False, 'error': 'Invalid request'}, status=400)
