"""
URL configuration for api_gateway project.
"""
from django.contrib import admin
from django.urls import path
from . import views
from .health import health, metrics

urlpatterns = [
    path('admin/', admin.site.urls),

    # Assignment 06 - Observability
    path('health/', health, name='health'),
    path('metrics/', metrics, name='metrics'),

    # Home
    path('', views.home, name='home'),

    # Unified login/logout
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.customer_register, name='register'),

    # Customer pages (kept for backward compat)
    path('customer/register/', views.customer_register, name='customer_register'),
    path('customer/login/', views.customer_login, name='customer_login'),
    path('customer/logout/', views.customer_logout, name='customer_logout'),
    path('customer/profile/', views.customer_profile, name='customer_profile'),

    # Staff pages
    path('staff/login/', views.staff_login, name='staff_login'),
    path('staff/logout/', views.staff_logout, name='staff_logout'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/books/', views.staff_books, name='staff_books'),
    path('staff/orders/', views.staff_orders, name='staff_orders'),
    path('staff/orders/<int:order_id>/status/', views.staff_update_order_status, name='staff_update_order_status'),
    path('staff/books/add/', views.staff_add_book, name='staff_add_book'),
    path('staff/books/<int:book_id>/edit/', views.staff_edit_book, name='staff_edit_book'),
    path('staff/books/<int:book_id>/delete/', views.staff_delete_book, name='staff_delete_book'),
    
    # Manager pages
    path('manager/login/', views.manager_login, name='manager_login'),
    path('manager/logout/', views.manager_logout, name='manager_logout'),
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/reports/', views.manager_reports, name='manager_reports'),
    
    # Book pages
    path('books/', views.book_list, name='book_list'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('books/<int:book_id>/rate_and_review/', views.rate_and_review_book, name='rate_and_review_book'),
    path('books/recommendations/', views.book_recommendations, name='book_recommendations'),
    
    # Cart pages
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:book_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:item_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    
    # Order pages
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/checkout/', views.checkout, name='checkout'),
    path('discount/validate/', views.validate_discount, name='validate_discount'),

    # AI Chat
    path('chat/', views.chat_page, name='chat'),
    path('chat/api/', views.chat_api, name='chat_api'),
]
