# 📦 라이브러리 불러오기
import os
import pickle
import torch
from dotenv import load_dotenv

from langchain.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient

from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain

# ✅ 0. 환경변수 로드 (.env 대신 env.txt 사용)
print('✅ 환경변수 로드')
env_path = '/content/env.txt'
load_dotenv(dotenv_path=env_path, override=True)
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ 1. 디바이스 설정 (Colab GPU 사용 최적화)
print('✅ Colab GPU 최적화 설정')
device = "cuda" if torch.cuda.is_available() else "cpu"

# ✅ 2. PDF → 문장 분할 + 페이지 범위 추정 + 캐싱
print('✅ PDF 문서 처리')
pdf_path = "/content/drive/MyDrive/data/한화생명 진심가득H보장보험 무배당_2126-A01~A03_약관_20250501~.pdf"
output_path = "/content/drive/MyDrive/data/split_docs.pkl"

if os.path.exists(output_path):
    print("✅ split_docs 캐시 불러오는 중...")
    with open(output_path, "rb") as f:
        split_docs = pickle.load(f)
else:
    print("📄 캐시 없음 → 문서 파싱 시작...")
    loader = UnstructuredPDFLoader(pdf_path, mode="elements")
    pages = loader.load()

    # 페이지별 텍스트 매핑
    page_map = [{"text": doc.page_content, "page": idx} for idx, doc in enumerate(pages, start=1)]

    # 문장 분할
    all_text = "\n".join([p["text"] for p in page_map])
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    split_texts = splitter.split_text(all_text)

    # 페이지 범위 추정 함수
    def find_page_range(text_chunk, page_map):
        page_nums = []
        for p in page_map:
            if text_chunk in p["text"]:
                return str(p["page"])
            for line in text_chunk.split("\n"):
                if line.strip() and line.strip() in p["text"]:
                    page_nums.append(p["page"])
                    break
        if not page_nums:
            return "unknown"
        elif len(set(page_nums)) == 1:
            return str(page_nums[0])
        else:
            return f"{min(page_nums)}-{max(page_nums)}"

    # 문서 객체 구성
    split_docs = [
        Document(page_content=chunk, metadata={"page_range": find_page_range(chunk, page_map)})
        for chunk in split_texts
    ]

    # 저장
    with open(output_path, "wb") as f:
        pickle.dump(split_docs, f)

    print(f"✅ 총 {len(split_docs)}개의 문서 저장됨 → {output_path}")
    print("🔍 첫 문서 예시:", split_docs[0].metadata, "\n", split_docs[0].page_content[:200])

# ✅ 3. 임베딩 모델 로드
print('✅ 임베딩 모델 로드 (BGE-M3 Korean)')
embedding_model = HuggingFaceEmbeddings(
    model_name="upskyy/bge-m3-korean",
    model_kwargs={"device": device}
)

# ✅ 4. Qdrant 업로드 or 재사용
collection_name = "insurance_docs"
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

if client.collection_exists(collection_name):
    print(f"✅ Qdrant 컬렉션 '{collection_name}' 재사용 중")
    vectorstore = Qdrant(
        collection_name=collection_name,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        embedding_function=embedding_model,
        prefer_grpc=False
    )
else:
    print(f"📦 Qdrant 컬렉션 '{collection_name}' 없음 → 문서 업로드 중...")
    vectorstore = Qdrant.from_documents(
        documents=split_docs,
        embedding=embedding_model,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=collection_name,
        prefer_grpc=False
    )
    print(f"✅ 총 {len(split_docs)}개 문서 업로드 완료!")

# ✅ 5. 대화형 QA 구성

# 메모리 (문맥 유지)
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# 프롬프트 설정
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "당신은 똑똑한 AI 보험설계사 어시스턴트입니다.\n"
        "다음 질문에 대해 관련 조항과 표를 함께 고려해서 논리적인 추론을 거쳐 정확히 답하세요.\n
표 내용은 구조적으로 분석하고, 해당 금액이나 조건을 명확히 전달해 주세요.\n"
        "참고: {context}\n"
        "질문: {question}\n"
        "답변:"
    )
)

# Retriever 구성
retriever = vectorstore.as_retriever()

# Conversational QA 체인 구성
print('# ✅ Conversational Retrieval QA 체인 구성')
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY),
    retriever=retriever,
    memory=memory,
    combine_docs_chain_kwargs={"prompt": prompt},
    return_source_documents=True
)

# ✅ 6. 질의 예시
query = "재해로 인해 장해가 생겼어 얼마 받을 수 있어?"
print('💬 질의:', query)
result = qa_chain({"question": query})

# ✅ 7. 결과 확인
print('📚 관련 문서:', result["source_documents"][0].metadata)
print("✅ 답변:", result["answer"])

# ✅ (선택) retriever 직접 확인
docs = retriever.get_relevant_documents(query)
print(f"🔍 벡터 검색으로 찾은 문서 수: {len(docs)}")
print("📄 첫 문서 preview:", docs[0].metadata, "\n", docs[0].page_content[:200])
