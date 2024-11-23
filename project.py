import os
from dotenv import load_dotenv
from datetime import datetime

import faiss
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.storage import LocalFileStore
from langchain.embeddings import CacheBackedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnableMap

# .env 파일 로드
load_dotenv()

# 환경 변수에서 API 키 불러오기 (이 부분은 통일되었으면 좋겠습니다. .evn API Key 저장방식을 사용했으면 좋겠습니다.)
api_key = os.getenv("OPENAI_API_KEY")




# 모델 초기화
model = ChatOpenAI(model="gpt-4o-mini")


# 파일 로드
file_path = " "
# PDF 파일 경로
loader = PyPDFLoader(file_path=file_path)

docs = loader.load()



# 파일 청킹
recursive_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=30,
    length_function=len,
    is_separator_regex=False,
)

splits = recursive_text_splitter.split_documents(docs)


# OpenAI 임베딩 모델 초기화
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


# 로컬 파일 저장소 설정
store = LocalFileStore("C:파일 저장경로")

# 캐시를 지원하는 임베딩 생성 - 임베딩시 계속 api 호출을 방지하기 위해 로컬에 임베팅 파일을 저장하는 형식
cached_embedder = CacheBackedEmbeddings.from_bytes_store(
    underlying_embeddings=embeddings,
    document_embedding_cache=store,
    namespace=embeddings.model,  # 기본 임베딩과 저장소를 사용하여 캐시 지원 임베딩을 생성
)
    
# FAISS를 이용한 벡터화
vectorstore = FAISS.from_documents(documents=splits, embedding=cached_embedder)

#retriever 정의
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3}) # 가져올 청크 수를 3으로 늘림

# 디버그 및 컨텍스트 처리 클래스

class DebugPassThrough(RunnablePassthrough):
    def invoke(self, *args, **kwargs):
        output = super().invoke(*args, **kwargs)
        print("Debug Output:", output)
        return output
# 문서 리스트를 텍스트로 변환하는 단계 추가
class ContextToText(RunnablePassthrough):
    def invoke(self, inputs, config=None, **kwargs):  # config 인수 추가
        # context의 각 문서를 문자열로 결합
        context_text = "\n".join([doc.page_content for doc in inputs["context"]])
        return {"context": context_text, "question": inputs["question"]}


# 프롬프트 파싱 함수 정의

def load_chat_prompt_template(prompt_path):
    '''
    프롬프트 경로에서 프롬프트 파일을 읽어 시스템 메시지와 사용자 메시지로 분리하고
    이를 사용하여 ChatPromptTemplate을 생성
    '''
    with open(prompt_path, 'r', encoding='utf-8') as file:
        prompt_text = file.read()
    # 'system'과 'human'으로 분리
    sections = prompt_text.strip().split('human') # 문자열 양쪽에 공백 제거 후, 'human'찾아 섹션을 나누고 리스트로 분리하기 

    # 정의 부분
    system_prompt = '' 
    user_prompt = ''
    if len(sections) == 2: # system과 human으로 분리되어 있을 때
        system_prompt = sections[0].replace('system', '').strip()
        user_prompt = sections[1].strip()
    else:
        user_prompt = prompt_text.strip() # 아니면 바로 user_prompt로 할당.
    # 메시지 리스트 생성
    messages = []
    if system_prompt:
        messages.append(("system", system_prompt))
    if user_prompt:
        messages.append(("user", user_prompt))
    # ChatPromptTemplate 생성
    prompt = ChatPromptTemplate.from_messages(messages)
    return prompt

# 체인 생성 함수
def create_rag_chain(prompt_template, retriever, model):
    chain = (
        RunnableMap({
            "question": DebugPassThrough(),
            "context": retriever
        })
        | ContextToText()
        | prompt_template
        | model
    )
    return chain


# 타임스탬프 생성
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
# 프롬프트 및 응답 폴더 설정
prompt_folder = 'Prompts'
prompt_files = [f for f in os.listdir(prompt_folder) if f.endswith('.txt')]
output_folder = 'responses'
os.makedirs(output_folder, exist_ok=True)

response = chain.invoke(query)
#print(type(response.content))  # <class 'dict'>

# 호출

while True:
    print("========================")
    query = input("질문을 입력하세요 (종료하려면 빈 줄 입력): ")
    if not query.strip():
        break
    for prompt_file in prompt_files:
        prompt_path = os.path.join(prompt_folder, prompt_file)
        prompt_template = load_chat_prompt_template(prompt_path)
        chain = create_rag_chain(prompt_template, retriever, model)
        print(f"\nUsing prompt from {prompt_file}")
        response = chain.invoke(query) # 문자열 요구 chain.invoke({"question": query}) -> chain.invoke(query) 수정
        print("Final Response:")
        print(response.content)
        # 응답 저장
        output_file = f"{os.path.splitext(prompt_file)[0]}_{timestamp}_result.txt"
        output_path = os.path.join(output_folder, output_file)
        with open(output_path, 'a', encoding='utf-8') as file:
            file.write("\nQuestion: " + query + "\nResponse: " + response.content + "\n")
        print(f"Response saved to {output_file}")