# bookstore/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('<int:pk>/', views.book_detail, name='book_detail'),
    path('<int:pk>/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    
    # ✅ 추가되는 장바구니 관련 엔드포인트
    path('<int:pk>/remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('<int:pk>/update-quantity/', views.update_quantity, name='update_quantity'),
    path('delete-selected/', views.delete_selected, name='delete_selected'),
    path('empty-cart/', views.empty_cart, name='empty_cart'),
    path('order/', views.order_page, name='order_page'),
    path('order/submit/', views.order_submit, name='order_submit'),
    path('orders/', views.order_list, name='order_list'),
    path('books/orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('books/orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('review/<int:book_id>/<int:order_id>/', views.write_review, name='write_review'),
]