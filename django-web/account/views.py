# views.py
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm  # 변경된 폼 import
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.html import escape
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth import authenticate
User = get_user_model()
class CustomLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 이메일 인증 여부 먼저 체크
        try:
            user = User.objects.get(username=username)
            if not user.is_active:
                messages.error(request, "이메일 인증이 완료되지 않았습니다. 인증 후 다시 로그인해주세요.")
                return redirect('account:login')
        except User.DoesNotExist:
            pass  # 존재하지 않으면 그냥 일반 실패 메시지로 진행

        # 정상 로그인 절차 진행
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        messages.error(self.request, "아이디 또는 비밀번호가 올바르지 않습니다.")
        return super().form_invalid(form)

def index(request):
    return render(request, 'account/account_index.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        print("폼 클래스:", form.__class__)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # 이메일 인증 전까지 비활성
            user.save()

            # 이메일 인증 링크 생성
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_link = request.build_absolute_uri(f"/account/activate/{uid}/{token}/")

            # 이메일 템플릿 렌더링
            subject = "이메일 인증을 완료해주세요"
            message = render_to_string('account/activation_email.html', {
                'user': user,
                'activation_link': activation_link,
            })

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            return HttpResponse(f"""
                <script>
                    alert("회원가입이 완료되었습니다!\\n이메일을 확인하여 인증을 완료해주세요.");
                    window.location.href = '{request.build_absolute_uri("/account/login/")}';
                </script>
            """)

        else:
            # 에러 메시지 처리
            error_list = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_list.append(f"{field}: {escape(error)}")
            error_msg = "\\n".join(error_list)

            return HttpResponse(f"""
                <script>
                    alert("회원가입에 실패했습니다:\\n{error_msg}");
                    window.history.back();
                </script>
            """)
    else:
        form = CustomUserCreationForm()
        print("폼 클래스:", form.__class__)

    return render(request, 'account/signup.html', {'form': form})

def activate(request, uidb64, token):  # 이용자가 이메일에서 인증 링크를 클릭하면 실행됨
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('이메일 인증이 완료되었습니다. 이제 로그인할 수 있습니다.')
    else:
        return HttpResponse('인증 링크가 유효하지 않거나 만료되었습니다.')