from django.shortcuts import render
from django.http import JsonResponse
import os
import re
from dotenv import load_dotenv
import logging
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
logger = logging.getLogger(__name__)

# Initialize LangChain components
def initialize_langchain(request):
    # Load environment variables
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=env_path, override=True)
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("API Key not found.")

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini")

    # Initialize Embeddings
    embeddings = OpenAIEmbeddings()

    # Sample documents for the vector store
  # 2️⃣ PDF 파일 로드
    pdf_path = "C:/Users/Admin/Documents/카카오톡 받은 파일/상권분석.pdf"
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()  # langchain Document 객체 리스트 반환

    print(f"🔍 PDF에서 {len(pages)}개의 페이지 로드됨")

    # 3️⃣ 긴 문서를 chunk로 분리
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.split_documents(pages)

    print(f"📝 {len(docs)}개의 문서 조각으로 분할 완료")


    # Create vector store
    vectorstore = FAISS.from_documents(docs, embeddings)
    retriever = vectorstore.as_retriever()

    # Get chat history from session or initialize empty
    chat_history = request.session.get('chat_history', [])
    
    # Create memory with chat history
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )
    
    # Load previous chat history into memory
    for message in chat_history:
        user_message = message.get('Human') or message.get('user')
        ai_message = message.get('AI') or message.get('ai')

        if user_message and ai_message:
            memory.chat_memory.add_user_message(user_message)
            memory.chat_memory.add_ai_message(ai_message)

    # Create prompt template
    prompt = PromptTemplate(
        input_variables=["chat_history", "context", "question"],
        template=(
            "당신은 똑똑한 AI 어시스턴트입니다.\n"
            "참고: {context}\n"
            "질문: {question}\n"
            "지금까지의 대화:\n{chat_history}\n"
            "답변:"
        )
    )

    # Create QA chain
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={"prompt": prompt},
        return_source_documents=True
    )

    return qa_chain

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

@csrf_exempt
def send(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': '메시지가 비어 있습니다.'}, status=400)

        try:
            # Initialize LangChain components with request
            qa_chain = initialize_langchain(request)

            # Get response from QA chain
            result = qa_chain.invoke({"question": user_message})
            bot_response = result['answer'].strip()

            # Update chat history in session
            chat_history = request.session.get('chat_history', [])
            chat_history.append({
                'Human': user_message,
                'AI': bot_response
            })
            request.session['chat_history'] = chat_history

            return JsonResponse({'response': format_response(bot_response)})

        except Exception as e:
            logger.error(f"Error in send view: {str(e)}", exc_info=True)
            return JsonResponse({'error': f'서버 오류: {str(e)}'}, status=500)

    return JsonResponse({'error': '잘못된 요청 방식입니다.'}, status=400)
