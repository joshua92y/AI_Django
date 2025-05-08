# gbook/views.py
from django.shortcuts import render, redirect
from .forms import GuestBookEntryForm
from django.shortcuts import get_object_or_404
from .models import GuestBookEntry,GuestBookFile
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import GuestBookEntryForm
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.db import transaction


def gbook_list(request):
    query = request.GET.get("q", "")
    if query:
        entries = GuestBookEntry.objects.filter(
            Q(title__icontains=query) | Q(message__icontains=query)
        ).order_by("-created_at")
    else:
        entries = GuestBookEntry.objects.all().order_by("-created_at")
    
    return render(request, "gbook/gbook_list.html", {"entries": entries})

@login_required
def gbook_create(request):
    try:
        User.objects.get(pk=request.user.pk)
    except User.DoesNotExist:
        logout(request)
        return redirect('account:login')

    if request.method == "POST":
        form = GuestBookEntryForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    entry = form.save(commit=False)
                    entry.author = request.user
                    entry.save()

                    for uploaded_file in request.FILES.getlist("files"):
                        GuestBookFile.objects.create(entry=entry, file=uploaded_file)

            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'ok': False, 'errors': str(e)}, status=500)
                else:
                    messages.error(request, '오류가 발생했습니다: ' + str(e))
                    return redirect('gbook_list')

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'ok': True,
                    'message': '작성되었습니다.',
                    'redirect_url': '/gbook/'
                })
            return redirect('gbook_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': False, 'errors': form.errors})
    else:
        form = GuestBookEntryForm()
    return render(request, 'gbook/gbook_form.html', {'form': form, 'is_edit': False})

def gbook_detail(request, pk):
    entry = get_object_or_404(GuestBookEntry, pk=pk)

    # ✅ 조회수 증가
    entry.views += 1
    entry.save(update_fields=["views"])

    return render(request, "gbook/gbook_detail.html", {"entry": entry})

@login_required
def gbook_edit(request, pk):
    entry = get_object_or_404(GuestBookEntry, pk=pk)

    if entry.author != request.user:
        messages.error(request, '수정 권한이 없습니다.')
        return redirect('gbook_detail', pk=entry.pk)

    if request.method == "POST":
        form = GuestBookEntryForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()

                    for uploaded_file in request.FILES.getlist("files"):
                        GuestBookFile.objects.create(entry=entry, file=uploaded_file)

            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'ok': False, 'errors': str(e)}, status=500)
                else:
                    messages.error(request, '오류가 발생했습니다: ' + str(e))
                    return redirect('gbook_list')

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'ok': True,
                    'message': '수정되었습니다.',
                    'redirect_url': '/gbook/'
                })
            return redirect('gbook_list')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': False, 'errors': form.errors})
    else:
        form = GuestBookEntryForm(instance=entry)

    return render(request, 'gbook/gbook_form.html', {'form': form, 'is_edit': True, 'entry': entry})
@login_required
@require_POST
def gbook_delete(request, pk):
    entry = get_object_or_404(GuestBookEntry, pk=pk)
    if entry.author != request.user:
        messages.error(request, '삭제 권한이 없습니다.')
        return redirect('gbook_detail', pk=entry.pk)
        
    entry.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'ok': True,
            'redirect_url': '/gbook/'
        })
    return redirect('gbook_list')
@require_POST
@login_required
def gbook_file_delete(request, pk):
    file = get_object_or_404(GuestBookFile, pk=pk)

    # 작성자만 삭제 가능
    if file.entry.author != request.user:
        return JsonResponse({'ok': False, 'error': '삭제 권한이 없습니다.'}, status=403)

    file.delete()
    return JsonResponse({'ok': True})