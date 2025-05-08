from django.shortcuts import render
from django.http import JsonResponse
import os
from dotenv import load_dotenv
import openai
import logging
import re
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

def format_response(text):
    # 줄바꿈 처리
    text = text.replace('\n', '<br>')
    
    # 이모지 처리 (이모지 유니코드 범위)
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    # 이모지가 있는 경우 그대로 유지
    if emoji_pattern.search(text):
        return mark_safe(text)
    
    # 긴 문장에 적절한 줄바꿈 추가
    sentences = text.split('. ')
    formatted_text = '. <br>'.join(sentences)
    
    return mark_safe(formatted_text)

def index(request):
    return render(request, 'AItest/chat.html')


def format_response(text):
    # 필요한 경우 HTML 이스케이프 등 처리
    return escape(text)

@csrf_exempt
def send(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': '메시지가 비어 있습니다.'}, status=400)

        try:
            # 🔐 .env에서 API 키 로드
            env_path = os.path.join(os.path.dirname(__file__), '.env')
            load_dotenv(dotenv_path=env_path, override=True)
            api_key = os.environ.get("OPENAI_API_KEY")

            if not api_key:
                return JsonResponse({'error': 'API Key를 불러오지 못했습니다.'}, status=500)

            client = openai.OpenAI(api_key=api_key)

            # ✅ 세션에서 대화 이력 불러오기
            chat_history = request.session.get('chat_history', [])

            # ✅ 새 메시지 추가
            chat_history.append({"role": "user", "content": user_message})

            # 이전까지 assistant 응답이 있었다면 포함
            # (chat_history 전체 전달 가능)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You are a helpful assistant."}] + chat_history,
            )

            bot_response = response.choices[0].message.content.strip()

            # ✅ 봇 응답을 이력에 추가
            chat_history.append({"role": "assistant", "content": bot_response})

            # ✅ 최대 10개 메시지만 기억 (원한다면 조정 가능)
            request.session['chat_history'] = chat_history[-10:]

            return JsonResponse({'response': format_response(bot_response)})

        except Exception as e:
            logger.error(f"Error in send view: {str(e)}", exc_info=True)
            return JsonResponse({'error': f'서버 오류: {str(e)}'}, status=500)

    return JsonResponse({'error': '잘못된 요청 방식입니다.'}, status=400)