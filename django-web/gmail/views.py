# views.py

from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

def index(request):
    return render(request, 'gmail/email_send.html')

def send_email(request):
    if request.method == 'POST':
        to_email = request.POST.get('to_email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
        )
        return HttpResponse('이메일이 성공적으로 전송되었습니다!')
    else:
        return render(request, 'gmail/email_send.html')
