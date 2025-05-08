# bookstore/views.py
from django.shortcuts import render, get_object_or_404,redirect
from django.core.paginator import Paginator
from .models import Book,UserProfile,Order, OrderItem
from django.db.models import Q
from django.http import JsonResponse,HttpResponseForbidden,HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from bookstore.models import Review

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    reviews = Review.objects.filter(book=book).select_related('reviewer')
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(reviewer=request.user).first()

    return render(request, 'bookstore/book_detail.html', {
        'book': book,
        'reviews': reviews,
        'user_review': user_review,
    })

def book_list(request):
    query = request.GET.get('q', '')  # 검색어 가져오기
    books = Book.objects.all()

    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )

    books = books.order_by('id')

    paginator = Paginator(books, 9)  # 한 페이지 9권
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'bookstore/books_list.html', {
        'page_obj': page_obj,
        'query': query,  # 검색어도 같이 넘겨야 함
    })
@csrf_exempt
def add_to_cart(request, pk):
    pk_str = str(pk)

    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))  # 🛒 quantity 받아오기, 없으면 1
    except (json.JSONDecodeError, TypeError, ValueError):
        quantity = 1

    if quantity <= 0:
        quantity = 1

    if request.user.is_authenticated:
        # 로그인 상태: UserProfile.cart에 저장
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_cart = profile.cart or {}

        if pk_str in user_cart:
            user_cart[pk_str] += quantity
        else:
            user_cart[pk_str] = quantity

        profile.cart = user_cart
        profile.save()
    else:
        # 비로그인 상태: 세션에 저장
        cart = request.session.get('cart', {})
        if pk_str in cart:
            cart[pk_str] += quantity
        else:
            cart[pk_str] = quantity
        request.session['cart'] = cart
    print("책번호:  ",pk_str,"수량:  ",quantity)
    return JsonResponse({'ok': True})

def cart_view(request):
    if request.user.is_authenticated:
        # ✅ 로그인 상태
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        cart = profile.cart or {}
    else:
        # ✅ 비로그인 상태
        cart = request.session.get('cart', {})

    # cart는 {'1': 2, '3': 1} 이런 식 (book_id: quantity)
    books = Book.objects.filter(id__in=[int(book_id) for book_id in cart.keys()])

    return render(request, 'bookstore/cart.html', {
        'books': books,
        'cart_quantities': cart,
    })
@csrf_exempt
def remove_from_cart(request, pk):
    pk_str = str(pk)
    if request.user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        cart = profile.cart or {}
        if pk_str in cart:
            del cart[pk_str]
            profile.cart = cart
            profile.save()
    else:
        cart = request.session.get('cart', {})
        if pk_str in cart:
            del cart[pk_str]
            request.session['cart'] = cart
    return JsonResponse({'ok': True})

@csrf_exempt
def update_quantity(request, pk):
    if request.method == 'POST':
        pk_str = str(pk)
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))

        if request.user.is_authenticated:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            cart = profile.cart or {}
            if quantity > 0:
                cart[pk_str] = quantity
            else:
                cart.pop(pk_str, None)  # 0이면 삭제
            profile.cart = cart
            profile.save()
        else:
            cart = request.session.get('cart', {})
            if quantity > 0:
                cart[pk_str] = quantity
            else:
                cart.pop(pk_str, None)
            request.session['cart'] = cart

        return JsonResponse({'ok': True})

@csrf_exempt
def delete_selected(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        ids = data.get('ids', [])

        if request.user.is_authenticated:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            cart = profile.cart or {}
            for book_id in ids:
                cart.pop(str(book_id), None)
            profile.cart = cart
            profile.save()
        else:
            cart = request.session.get('cart', {})
            for book_id in ids:
                cart.pop(str(book_id), None)
            request.session['cart'] = cart

        return JsonResponse({'ok': True})

@csrf_exempt
def empty_cart(request):
    if request.user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.cart = {}
        profile.save()
    else:
        request.session['cart'] = {}

    return JsonResponse({'ok': True})
@receiver(user_logged_in)
def merge_carts(sender, request, user, **kwargs):
    session_cart = request.session.get('cart', {})  # 세션 카트
    profile, created = UserProfile.objects.get_or_create(user=user)  # UserProfile 가져오기
    user_cart = profile.cart or {}  # DB 카트

    # ✅ 세션 cart가 비어있지 않을 때만 합치기
    if session_cart:
        for pk_str, qty in session_cart.items():
            if pk_str in user_cart:
                user_cart[pk_str] += qty
            else:
                user_cart[pk_str] = qty

        # 업데이트 저장
        profile.cart = user_cart
        profile.save()

    # 세션 cart는 항상 비워주기
    request.session['cart'] = {}

@csrf_exempt
def order_page(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)

        books_data = data.get('books', [])  # [{id: 1, quantity: 2}, ...]

        order_books = []
        total_price = 0

        for item in books_data:
            book = Book.objects.get(pk=item['id'])
            quantity = int(item['quantity'])
            total = book.price * quantity
            order_books.append({
                'book': book,
                'quantity': quantity,
                'subtotal': total
            })
            total_price += total

        return render(request, 'bookstore/order_page.html', {
            'items': order_books,           # ✅ 템플릿과 맞춤
            'total_price': total_price,
        })

    return redirect('book_list')

@csrf_exempt
@login_required
def order_submit(request):
    if request.method == 'POST':
        book_ids = request.POST.getlist('books')  # ['1:2', '3:1']

        if not book_ids:
            return redirect('book_list')

        try:
            with transaction.atomic():
                order = Order.objects.create(user=request.user)

                for book_id in book_ids:
                    quantity = int(request.POST.get(f'quantity_{book_id}', 1))
                    book = get_object_or_404(Book, pk=book_id)
                    OrderItem.objects.create(order=order, book=book, quantity=quantity)

                # ✅ 주문과 동시에 장바구니 비우기
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.cart = {}
                profile.save()

        except Exception as e:
            print("❌ 주문 처리 중 오류:", e)
            return redirect('cart')  # 실패 시 장바구니로 보내버리기

        return render(request, 'bookstore/order_success.html', {
            'order': order,
        })
    else:
        return redirect('book_list')

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(orders, 5)  # 5개씩 끊기
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'bookstore/order_list.html', {
        'orders': page_obj
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # 이 주문에서 리뷰한 책들
    reviews = Review.objects.filter(reviewer=request.user, order=order)
    review_map = {}
    for r in reviews:
        review_map[r.book.id] = r

    order_items = []
    for item in order.items.all():
        review = review_map.get(item.book.id)
        order_items.append((item, review))  # 튜플로 묶어서 넘김

    return render(request, 'bookstore/order_detail.html', {
        'order': order,
        'order_items': order_items,
    })
@require_POST
@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    try:
        with transaction.atomic():
            order.status = 'cancelled'  # ✅ 상태 변경
            order.save()
    except Exception as e:
        print("❌ 주문 취소 중 오류:", e)

    return redirect('order_list')

@login_required
@require_POST
def write_review(request, book_id, order_id):
    book = get_object_or_404(Book, id=book_id)
    order = get_object_or_404(Order, id=order_id, user=request.user)

    has_ordered = OrderItem.objects.filter(order=order, book=book).exists()
    if not has_ordered:
        return HttpResponseForbidden("리뷰를 남길 수 없는 책입니다.")

    already_reviewed = Review.objects.filter(book=book, reviewer=request.user, order=order).exists()
    if already_reviewed:
        return HttpResponseBadRequest("이미 이 주문에 리뷰를 작성했습니다.")

    Review.objects.create(
        book=book,
        order=order,
        reviewer=request.user,
        rating=int(request.POST.get("rating")),
        comment=request.POST.get("comment")
    )
    return redirect("order_detail", order_id=order.id)

@login_required
@require_POST
def write_or_edit_review(request, book_id, order_id):
    book = get_object_or_404(Book, id=book_id)
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if not OrderItem.objects.filter(order=order, book=book).exists():
        return HttpResponseForbidden("리뷰 남길 수 없는 항목입니다.")

    review, created = Review.objects.get_or_create(
        book=book,
        order=order,
        reviewer=request.user,
        defaults={'rating': request.POST.get('rating'), 'comment': request.POST.get('comment')}
    )

    if not created:
        # 이미 있으면 수정
        review.rating = request.POST.get("rating")
        review.comment = request.POST.get("comment")
        review.save()

    return redirect("order_detail", order_id=order.id)