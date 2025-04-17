# store/views.py
from django.shortcuts import render, redirect
from .models import Product
import pickle, os
from datetime import datetime
from django.http import JsonResponse

PRODUCT_FILE = 'C:/test/store/products.pkl'

def load_products():
    if os.path.exists(PRODUCT_FILE):
        with open(PRODUCT_FILE, 'rb') as f:
            return pickle.load(f)
    return []

def save_products(products):
    os.makedirs(os.path.dirname(PRODUCT_FILE), exist_ok=True)
    with open(PRODUCT_FILE, 'wb') as f:
        pickle.dump(products, f)

def product_add(request):
    if request.method == 'POST':
        number = int(request.POST['number'])
        name = request.POST['name']
        price = int(request.POST['price'])
        manufacturer = request.POST['manufacturer']
        made_date = datetime.strptime(request.POST['made_date'], '%Y-%m-%d').date()

        new_product = Product(number, name, price, manufacturer, made_date)
        products = load_products()
        products.append(new_product)
        save_products(products)
        return redirect('product_list')
    
    return render(request, 'store/product_add.html')

def product_detail_or_list(request):
    id_param = request.GET.get('id')
    if id_param and id_param.isdigit():
        number = int(id_param)
        products = load_products()
        product = next((p for p in products if p.number == number), None)
        if product:
            return render(request, 'store/product_detail.html', {'product': product})
        else:
            return render(request, 'store/product_not_found.html', status=404)
    
    # ?id 없으면 리스트로 fallback
    return redirect('product_list')
def product_search_list(request):
    query = request.GET.get('q', '').strip().lower()
    products = load_products()

    if query:
        products = [
            p for p in products if
            query in p.name.lower() or
            query in p.manufacturer.lower() or
            query in str(p.number)
        ]

    return render(request, 'store/product_list.html', {
        'products': products,
        'search_query': query,
    })
def product_detail_by_query(request):
    id_param = request.GET.get('id')
    if not id_param or not id_param.isdigit():
        return render(request, 'store/product_not_found.html', status=404)

    number = int(id_param)
    products = load_products()
    product = next((p for p in products if p.number == number), None)

    if not product:
        return render(request, 'store/product_not_found.html', status=404)

    return render(request, 'store/product_detail.html', {'product': product})

def product_delete(request):
    number = request.GET.get('id')
    if not number or not number.isdigit():
        return JsonResponse({'success': False, 'error': 'Invalid ID'})

    number = int(number)
    products = load_products()
    products = [p for p in products if p.number != number]
    save_products(products)
    return JsonResponse({'success': True})

def product_edit(request):
    id_param = request.GET.get('id')
    if not id_param or not id_param.isdigit():
        return render(request, 'store/product_not_found.html', status=404)

    number = int(id_param)
    products = load_products()
    product = next((p for p in products if p.number == number), None)

    if not product:
        return render(request, 'store/product_not_found.html', status=404)

    if request.method == 'POST':
        product.name = request.POST['name']
        product.price = int(request.POST['price'])
        product.manufacturer = request.POST['manufacturer']
        product.made_date = datetime.strptime(request.POST['made_date'], '%Y-%m-%d').date()

        for i, p in enumerate(products):
            if p.number == number:
                products[i] = product
                break
        save_products(products)

        # ✅ 수정 완료 후 상세페이지로 리다이렉트
        return redirect(f'/store/detail/?id={number}')

    return render(request, 'store/product_edit.html', {'product': product})