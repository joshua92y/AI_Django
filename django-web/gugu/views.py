# gugu/views.py
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

def gugu(request, dan):
    result = ""
    for i in range(1, 10):
        result += f"{dan} x {i} = {dan * i}<br>"
    return HttpResponse(result)

# gugu/views.py
def gugu_template_view(request, dan):
    results = [f"{dan} x {i} = {dan * i}" for i in range(1, 10)]
    context = {
        'dan': dan,
        'results': results
    }
    return render(request, 'gugu/gugu_result.html', context)

def ajax_page(request):
    return render(request, 'gugu/gugu_ajax.html')

def ajax_gugu(request, dan):
    dan = int(dan)
    result = [f"{dan} x {i} = {dan * i}" for i in range(1, 10)]
    return JsonResponse({'result': result})

@require_POST
def add_numbers(request):
    try:
        num1 = int(request.POST.get('num1'))
        num2 = int(request.POST.get('num2'))
        result = num1 + num2
        return JsonResponse({'result': result})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def add_ajax_view(request):
    return render(request, 'gugu/add_ajax.html')